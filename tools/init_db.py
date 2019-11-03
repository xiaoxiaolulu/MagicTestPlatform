from peewee import MySQLDatabase
from apps.communities.models import CommunityGroup, CommunityGroupMember, PostComment, Post
from apps.project.models import Project, FunctionGenerator, TestEnvironment
from apps.users.models import User
from MagicTestPlatform.settings import database, settings


database = MySQLDatabase(
    database=settings['db']['name'], host=settings['db']['host'], port=settings['db']['port'], user=settings['db']['user'],
    password=settings['db']['password']
)


def init():
    # database.create_tables([User, ])
    # database.create_tables([CommunityGroup, CommunityGroupMember, Post, PostComment])
    database.create_tables([Project, FunctionGenerator, TestEnvironment])


if __name__ == '__main__':
    init()
