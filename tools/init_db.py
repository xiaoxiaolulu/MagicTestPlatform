from peewee import MySQLDatabase
from apps.interface_test.models import Interfaces
from apps.project.models import (
    Project,
    FunctionGenerator,
    TestEnvironment,
    DBSetting
)
from apps.users.models import User
from MagicTestPlatform.settings import database_async
from apps.utils.parse_settings import settings


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
    database_async.create_tables([Interfaces, ])


if __name__ == '__main__':
    init()
