import urllib3
from urllib import parse
import requests
import simplejson
from requests import exceptions
from apps.utils.Recursion import GetJsonParams

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class BaseKeyWords(GetJsonParams):

    def __init__(self, request_body: dict):
        self.request_body = request_body

    @staticmethod
    def post(**kwargs: dict) -> requests.Response:
        r"""发送POST请求。返回:class:`Response` object。

        :Args:
         - \*\*kwargs:: “session.post”接受的可选参数。

        :Usage:
            post(url='/admin/category/add', data={"name": "AUTO", "enabled": 1})
        """
        return requests.post(verify=False, **kwargs)

    @staticmethod
    def get(**kwargs: dict) -> requests.Response:
        r"""发送GET请求。返回:class:`Response` object。

        :Args:
         - \*\*kwargs:: “session.get”接受的可选参数

        :Usage:
            get(url='/admin/category/getNames')
        """
        return requests.get(**kwargs, verify=False)

    def make_test_templates(self) -> dict:
        r"""创建测试用例的基础数据

        :Usage:
            make_test_templates()
        """
        method = GetJsonParams.get_value(self.request_body, 'method')

        if method in ['get', 'GET']:
            temp = ('url', 'params', 'headers', 'timeout')
            request_body = GetJsonParams.for_keys_to_dict(*temp, my_dict=self.request_body)
            if request_body['params']:
                if '=' in request_body.get('params') or '&' in request_body.get('params'):
                    request_body['params'] = dict(parse.parse_qsl(request_body['params']))

            try:
                response = self.get(**request_body)
                try:
                    response_body = response.json()
                except simplejson.JSONDecodeError:
                    response_body = response.text
                return {
                    "status_code": response.status_code,
                    "response_body": response_body
                }
            except exceptions.Timeout as error:
                raise error

        if method in ['post', 'POST']:
            temp = ('url', 'headers', 'json', 'data', 'files', 'timeout')
            request_body = GetJsonParams.for_keys_to_dict(*temp, my_dict=self.request_body)

            try:
                response = self.post(**request_body)
                try:
                    response_body = response.json()
                except simplejson.JSONDecodeError:
                    response_body = response.text
                return {
                    "status_code": response.status_code,
                    "response_body": response_body
                }
            except exceptions.Timeout as error:
                raise error
        else:
            raise Exception("接口测试请求类型错误, 请检查相关用例!")
