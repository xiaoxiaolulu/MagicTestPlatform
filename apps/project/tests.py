"""
    项目管理模块
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import unittest
from tornado.testing import AsyncHTTPTestCase
import server


class ProjectModuleTestCases(AsyncHTTPTestCase):

    def get_app(self):
        return server.app

    def test_main(self):
        response = self.fetch('/test_envs/')
        print(response)


if __name__ == '__main__':
    unittest.main()
