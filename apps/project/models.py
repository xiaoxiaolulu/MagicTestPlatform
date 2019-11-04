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


class TestEnvironment(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="测试环境名称")
    creator = ForeignKeyField(User, verbose_name="环境创建者")
    host_address = CharField(max_length=50, null=True, verbose_name="环境地址")
    desc = TextField(verbose_name="环境描述")
    
    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)


class DBSetting(BaseModel):
    
    name = CharField(max_length=50, null=True, verbose_name="数据库名称")
    creator = ForeignKeyField(User, verbose_name="数据库创建者")
    db_type = CharField(max_length=20, null=True, verbose_name="数据库类型")
    db_user = CharField(max_length=20, null=True, verbose_name='数据库账号')
    db_password = CharField(max_length=30, null=True, verbose_name="数据库密码")
    db_host = CharField(max_length=30, null=True, verbose_name="数据库地址")
    db_port = IntegerField(null=True, verbose_name="数据库端口号")
    desc = TextField(verbose_name="数据库描述")
    
    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)
