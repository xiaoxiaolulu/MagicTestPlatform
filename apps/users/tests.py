"""
    用户模块测试
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import requests
import unittest


class UserModulesTestCase(unittest.TestCase):

    Route = 'http://127.0.0.1:8081'

    def test_send_verification_code_success(self):
        """验证码发送成功"""
        test_route = f"{self.Route}/code/"
        data = {'account': "546464268@qq.com"}
        response = requests.post(test_route, json=data)
        print(response.text)
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        """注册成功"""
        test_route = f"{self.Route}/register/"
        data = {
            'account': "546464268@qq.com",
            "code": 1231,
            "password": 'qaz@wsx.123'
        }
        response = requests.post(test_route, json=data)
        print(response.text)
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """登录成功"""
        test_route = f"{self.Route}/login/"
        data = {
            'account': "546464268@qq.com",
            "password": '123456'
        }
        response = requests.post(test_route, json=data)
        print(response.text)
        self.assertEqual(response.status_code, 200)

    def test__rest_password_success(self):
        """重置密码成功"""
        test_route = f"{self.Route}/rest/"
        data = {
            "mobile": "13564957379",
            "code": "4542",
            "password": 'qaz@wsx.123'
        }
        response = requests.post(test_route, json=data)
        print(response.text)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
