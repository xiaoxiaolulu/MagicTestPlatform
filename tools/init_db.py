import sys
import environ
root = (environ.Path(__file__) - 2)
sys.path.append(str(root))
from peewee import MySQLDatabase
from apps.interface_test.models import (
    Interfaces,
    TestCases,
    InterfacesTestCase,
    CheckDbContent,
    PublicParams,
    TestSuite,
    TestCaseSuite
)
from apps.project.models import (
    Project,
    FunctionGenerator,
    TestEnvironment,
    DBSetting
)
from apps.web_ui_test.models import (
    PageElement
)
from apps.test_tools.models import (
    ImageIdentifyText
)
from apps.users.models import User
from settings.base import database_async
from common.parse_settings import settings


database = MySQLDatabase(
    database=settings.DATABASES.NAME,
    host=settings.DATABASES.HOST,
    port=settings.DATABASES.PORT,
    user=settings.DATABASES.USER,
    password=settings.DATABASES.PASSWORD
)


def init():
    database_async.create_tables([User, ])
    database_async.create_tables(
        [
            Project,
            FunctionGenerator,
            TestEnvironment,
            DBSetting
        ]
    )
    database_async.create_tables(
        [
            Interfaces,
            TestCases,
            InterfacesTestCase,
            CheckDbContent,
            PublicParams,
            TestSuite,
            TestCaseSuite
        ]
    )
    database_async.create_tables([ImageIdentifyText])
    database_async.create_tables([PageElement])


if __name__ == '__main__':
    init()
