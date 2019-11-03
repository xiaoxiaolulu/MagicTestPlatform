from peewee import *
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


class Project(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="名称")
    creator = ForeignKeyField(User, verbose_name="创建者")
    desc = TextField(verbose_name="描述")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)


class FunctionGenerator(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="名称")
    creator = ForeignKeyField(User, verbose_name="创建者")
    function = CharField(max_length=200, null=True, verbose_name="函数文件")
    desc = TextField(verbose_name="描述")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)
