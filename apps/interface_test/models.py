"""
    接口测试模块数据库模型
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from peewee import *
from peewee import CharField
from playhouse.fields import ManyToManyField
from MagicTestPlatform.models import BaseModel
from apps.project.models import (
    Project,
    DBSetting
)
from apps.users.models import User


class Interfaces(BaseModel):

    interface_name = CharField(max_length=50, null=True, verbose_name='接口名称')
    url = CharField(max_length=252, null=True, verbose_name="请求路由")
    method = CharField(max_length=25, null=True, verbose_name="请求方法")
    headers = CharField(max_length=252, null=True, verbose_name="请求头部")
    params = TextField(null=True, verbose_name="请求参数")
    creator = ForeignKeyField(User, verbose_name="创建者")
    project = ForeignKeyField(Project, verbose_name='项目配置')
    desc = TextField(verbose_name="接口描述")

    @classmethod
    def extend(cls):
        return cls.select(
            cls,
            User.id,
            User.nick_name,
            Project.name) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator).switch(cls) \
            .join(Project, join_type=JOIN.LEFT_OUTER, on=cls.project)


class TestCases(BaseModel):

    test_name = CharField(max_length=50, null=True, verbose_name="用例名称")
    interfaces = ManyToManyField(Interfaces)
    response = TextField(null=True, verbose_name="请求结果")
    assertion = TextField(null=True, verbose_name="断言数据")
    db = ForeignKeyField(DBSetting, verbose_name="数据库配置")
    check_db = TextField(null=True, verbose_name="落库校验")
    creator = ForeignKeyField(User, verbose_name="创建者")
    desc = TextField(verbose_name="用例描述")

    @classmethod
    def extend(cls):
        return cls.select(
            cls,
            User.id,
            User.nick_name,
            Interfaces.id,
            Interfaces.interface_name,
            Interfaces.url,
            Interfaces.method,
            Interfaces.headers,
            Interfaces.params,
            Interfaces.project,
            DBSetting.id,
            DBSetting.db_type,
            DBSetting.db_host,
            DBSetting.db_user,
            DBSetting.db_password,
            DBSetting.db_port,
            DBSetting.name) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator).switch(cls) \
            .join(Interfaces, join_type=JOIN.LEFT_OUTER, on=cls.interfaces)\
            .join(DBSetting, join_type=JOIN.LEFT_OUTER, on=cls.db)


InterfacesTestCase = TestCases.interfaces.get_through_model()


class VariableDependency(BaseModel):

    response_extraction = TextField(null=True, verbose_name="临时提取变量")
