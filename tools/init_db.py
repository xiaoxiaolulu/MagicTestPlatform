from peewee import MySQLDatabase

from apps.interface_test.models import Interfaces
from apps.project.models import Project, FunctionGenerator, TestEnvironment, DBSetting
from apps.users.models import User
from MagicTestPlatform.settings import database, settings


database = MySQLDatabase(
    database=settings['db']['name'], host=settings['db']['host'], port=settings['db']['port'], user=settings['db']['user'],
    password=settings['db']['password']
)


def init():
    # database.create_tables([User, ])
    # database.create_tables([Project, FunctionGenerator, TestEnvironment, DBSetting])
    database.create_tables([Interfaces, ])


if __name__ == '__main__':
    init()
