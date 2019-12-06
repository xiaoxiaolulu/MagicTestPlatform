import unittest
from playhouse.shortcuts import model_to_dict
from apps.interface_test.models import TestCases, Interfaces


class InterfaceModelsTest(unittest.TestCase):

    def test_all(self):
        case = TestCases.get(TestCases.test_name == "测试")

        case.interfaces.add([
            Interfaces.get(Interfaces.interface_name == '李四'),
            Interfaces.get(Interfaces.interface_name == '王五')])


if __name__ == '__main__':
    unittest.main()