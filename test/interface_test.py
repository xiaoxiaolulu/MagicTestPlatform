import sys
import environ
root = (environ.Path(__file__) - 2)
sys.path.append(str(root))
import unittest
from playhouse.shortcuts import model_to_dict
from apps.interface_test.models import TestCases, Interfaces


class InterfaceModelsTest(unittest.TestCase):

    def test_all(self):
        case = TestCases.get(TestCases.test_name == "测试")

        case.interfaces.add([10, 11])


if __name__ == '__main__':
    unittest.main()