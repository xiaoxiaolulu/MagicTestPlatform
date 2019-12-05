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

    account = randint(100000, 200000)

    def get_app(self):
        return HTTPServer(server.Application(), xheaders=True)

    def test_verification_code(self):
        body = json.dumps({"account": f"{self.account}@163.com"})
        response = self.fetch('/code/', method='POST', body=body)
        response = json.loads(response.body.decode())
        self.assertEqual(response.get('code'), 1)
        self.assertEqual(response.get('msg'), '验证码已发送，请注意接收〜')

    def test_register(self):
        register_body = json.dumps({"account": f"{self.account}@163.com", "code": f"{111}", "password": "123456"})
        register_response = self.fetch('/register/', method='POST', body=register_body)
        register_response = json.loads(register_response.body.decode())
        self.assertEqual(register_response.get('code'), 1)
        self.assertEqual(register_response.get('msg'), '账号注册成功')

    def test_login_success(self):
        body = json.dumps({"account": "123456@163.com", "password": "123456"})
        response = self.fetch('/login/', method='POST', body=body)
        response = json.loads(response.body.decode())
        self.assertEqual(response.get('code'), 1)
        self.assertEqual(response.get('data').get('nick_name'), '123456@163.com')


if __name__ == '__main__':
    unittest.main()
