import json
import functools
from random import choice
import base64
import requests
import jwt
import paramiko
from urllib.parse import urlencode
from tornado import httpclient
from tornado.httpclient import HTTPRequest
from apps.users.models import User
from common.parse_settings import settings


def generate_code():
    """
    生成随机4位数字的验证码
    """
    seeds = "1234567890"
    return "".join(
        [choice(seeds) for index in range(4)]
    )


def python_running_env(code: str) -> str:
    """
    python 代码运行环境
    :param code: python代码
    """

    def sftp_exec_command(client, command):
        try:
            std_in, std_out, std_err = client.exec_command(command, timeout=4)
            out = "".join([line for line in std_out])
            return out
        except Exception as msg:
            return msg

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        settings.CODE_DEBUG.HOST,
        settings.CODE_DEBUG.PORT,
        settings.CODE_DEBUG.USER,
        settings.CODE_DEBUG.PASSWORD
    )

    sftp_exec_command(ssh_client, "touch test.py")
    sftp_exec_command(ssh_client, f"echo \"{code}\" > test.py")
    response = sftp_exec_command(ssh_client, "python test.py")
    sftp_exec_command(ssh_client, "rm -rf test.py")
    ssh_client.close()
    return response


def image_identifying_text(filepath: str) -> requests.Response:
    """
    图片识别文字
    :param filepath:  图片路径地址
    """

    token = requests.get(settings.BAIDUCE_AUTH).json().get('access_token')
    address = settings.BAIDUCE_API + "?access_token=" + token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    stream = {"image": base64.b64encode(open(filepath, 'rb').read())}
    res_data = requests.post(address, data=stream, headers=headers)
    return res_data.json()


async def async_image_identifying_text(filepath: str) -> requests.Response:
    """
    异步方法-图片识别文字
    :param filepath:  图片路径地址
    """
    http_client = httpclient.AsyncHTTPClient()
    token = requests.get(settings.BAIDUCE_AUTH).json().get('access_token')
    address = settings.BAIDUCE_API + "?access_token=" + token
    stream = {"image": base64.b64encode(open(filepath, 'rb').read())}
    post_request = HTTPRequest(url=address, method="POST", body=urlencode(stream))
    try:
        res = await http_client.fetch(post_request)
        res_data = json.loads(res.body.decode("utf8"))
    except Exception as msg:
        res_data = {"code": 0, "msg": f"{msg}"}
    return res_data


def format_arguments(arguments):
    """
    以request.body_arguments 或者 request.arguments传参时
    将二进制转化utf-8编码
    :param arguments:
    :return:
    """

    data = {
        k: list(
            map(
                lambda val: str(val, encoding="utf-8"),
                v
            )
        )
        for k, v in arguments.items()
    }
    return data


def authenticated_async(method):

    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        authorization = self.request.headers.get('Authorization', None)
        if authorization:
            try:
                jwt_data = jwt.decode(
                    authorization,
                    settings.TORNADO_CONF.secret_key,
                    leeway=settings.TORNADO_CONF.jwt_expire,
                    options={"verify_exp": True}
                )

                user_id = jwt_data["id"]
                # 从数据库中获取到user并设置给_current_user
                try:
                    user = await self.application.objects.get(User, id=user_id)
                    self._current_user = user
                    await method(self, *args, **kwargs)
                except User.DoesNotExist:
                    self.set_status(401)
            except jwt.ExpiredSignatureError:
                self.set_status(401)
        else:
            self.set_status(401)
            self.finish({})
    return wrapper


class Route(object):
    """ 把每个URL与Handler的关系保存到一个元组中，然后追加到列表内，列表内包含了所有的Handler """

    def __init__(self):
        # 路由列表
        self.urls = list()

    def __call__(self, url, *args, **kwargs):
        def register(cls):
            # 把路由的对应关系表添加到路由列表中
            self.urls.append((url, cls))
            return cls

        return register


route = Route()
