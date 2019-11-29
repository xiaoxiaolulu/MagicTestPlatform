"""
    用户模块测试
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import json
import unittest
from random import randint
from tornado.httpserver import HTTPServer
from tornado.testing import AsyncHTTPTestCase
import server


class UserModuleTest(AsyncHTTPTestCase):

    def get_app(self):
        return HTTPServer(server.Application(), xheaders=True)

    def test_verification_code(self):
        body = json.dumps({"account": f"{randint(100000, 200000)}@163.com"})
        response = self.fetch('/code/', method='POST', body=body)
        response = json.loads(response.body.decode())
        UserModuleTest.code = response.get('data').get('VerCode')
        self.assertEqual(response.get('code'), 1)
        self.assertEqual(response.get('msg'), '验证码已发送，请注意接收〜')

    def test_login_success(self):
        body = json.dumps({"account": "123456@163.com", "password": "123456"})
        response = self.fetch('/login/', method='POST', body=body)
        response = json.loads(response.body.decode())
        self.assertEqual(response.get('code'), 1)
        self.assertEqual(response.get('data').get('nick_name'), '123456@163.com')


if __name__ == '__main__':
    unittest.main()
