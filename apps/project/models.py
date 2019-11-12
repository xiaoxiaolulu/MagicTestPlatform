"""
    项目管理模块数据库模型
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from peewee import *
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


class FunctionGenerator(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="名称")
    creator = ForeignKeyField(User, verbose_name="创建者")
    function = CharField(max_length=200, null=True, verbose_name="函数方法")
    desc = TextField(verbose_name="描述")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)

    def __init__(self, name: CharField = None, creator: ForeignKeyField = None, function: CharField = None,
                 desc: TextField = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: CharField = name
        self.creator: ForeignKeyField = creator
        self.function: CharField = function
        self.desc: TextField = desc


class TestEnvironment(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="测试环境名称")
    creator = ForeignKeyField(User, verbose_name="环境创建者")
    host_address = CharField(max_length=50, null=True, verbose_name="环境地址")
    desc = TextField(verbose_name="环境描述")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)

    def __init__(self, name: CharField = None, creator: ForeignKeyField = None, host_address: CharField = None,
                 desc: TextField = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: CharField = name
        self.creator: ForeignKeyField = creator
        self.host_address: CharField = host_address
        self.desc: TextField = desc


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

    def __init__(
            self,
            name: CharField = None,
            creator: ForeignKeyField = None,
            db_type: CharField = None,
            db_user: CharField = None,
            db_password: CharField = None,
            db_host: CharField = None,
            db_port: IntegerField = None,
            desc: TextField = None,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.name: CharField = name
        self.creator: ForeignKeyField = creator
        self.db_type: CharField = db_type
        self.db_user: CharField = db_user
        self.db_password: CharField = db_password
        self.db_host: CharField = db_host
        self.db_port: IntegerField = db_port
        self.desc: TextField = desc


class Project(BaseModel):

    name = CharField(max_length=50, null=True, verbose_name="名称")
    env = ForeignKeyField(TestEnvironment, verbose_name="环境配置")
    creator = ForeignKeyField(User, verbose_name="创建者")
    desc = TextField(verbose_name="描述")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name, TestEnvironment.name, TestEnvironment.host_address)\
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator) .switch(cls)\
            .join(TestEnvironment, join_type=JOIN.LEFT_OUTER, on=cls.env)

    def __init__(
            self,
            name: CharField = None,
            env: ForeignKeyField = None,
            creator: ForeignKeyField = None,
            desc: TextField = None,
            *args,
            **kwargs):
        super().__init__(*args, **kwargs)
        self.name: CharField = name
        self.env: ForeignKeyField = env
        self.creator: ForeignKeyField = creator
        self.desc: TextField = desc
