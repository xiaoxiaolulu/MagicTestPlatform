import functools
from random import choice
import jwt
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


class Response(object):

    def __init__(self, code=0, msg="", data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def json(self):
        return {
            "code": self.code,
            "msg": self.msg,
            "data": self.data
        }


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


if __name__ == '__main__':
    print(generate_code())