from peewee import MySQLDatabase
from apps.interface_test.models import (
    Interfaces,
    TestCases,
    InterfacesTestCase,
    CheckDbContent
)
try:
    from common.parse_settings import settings
    from settings.base import database_async
except (ImportError, ModuleNotFoundError):
    import sys
    import environ
    root = (environ.Path(__file__) - 2)
    sys.path.append(str(root))
    from common.parse_settings import settings
    from settings.base import database_async


database = MySQLDatabase(
    database=settings.DATABASES.NAME,
    host=settings.DATABASES.HOST,
    port=settings.DATABASES.PORT,
    user=settings.DATABASES.USER,
    password=settings.DATABASES.PASSWORD
)


def init():
    # database_async.create_tables([User, ])
    # database_async.create_tables([Project, FunctionGenerator, TestEnvironment, DBSetting])
    database_async.create_tables([Interfaces, TestCases, InterfacesTestCase, CheckDbContent])


if __name__ == '__main__':
    init()

