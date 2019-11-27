"""
    接口测试模块数据库模型
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from peewee import *
from peewee import CharField
from MagicTestPlatform.models import BaseModel
from apps.project.models import Project, DBSetting
from apps.users.models import User


class Interfaces(BaseModel):

    interface_name = CharField(max_length=50, null=True, verbose_name='接口名称')
    url = CharField(max_length=252, null=True, verbose_name="请求路由")
    method = CharField(max_length=25, null=True, verbose_name="请求方法")
    headers = CharField(max_length=252, null=True, verbose_name="请求头部")
    params = CharField(max_length=252, null=True, verbose_name="请求参数")
    assertion = CharField(max_length=252, null=True, verbose_name="断言数据")
    db = ForeignKeyField(DBSetting, verbose_name="数据库配置")
    check_db = CharField(max_length=252, null=True, verbose_name="落库校验")
    response_extraction = CharField(max_length=252, null=True, verbose_name="返回值提取")
    creator = ForeignKeyField(User, verbose_name="创建者")
    project = ForeignKeyField(Project, verbose_name='项目配置')
    desc = TextField(verbose_name="接口描述")

    @classmethod
    def extend(cls):
        return cls.select(
            cls,
            User.id,
            User.nick_name,
            DBSetting.name,
            DBSetting.db_type,
            DBSetting.db_host,
            DBSetting.db_password,
            DBSetting.db_user,
            DBSetting.db_port,
            Project.name) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator).switch(cls) \
            .join(DBSetting, join_type=JOIN.LEFT_OUTER, on=cls.db).switch(cls) \
            .join(Project, join_type=JOIN.LEFT_OUTER, on=cls.project)


class VariableDependency(BaseModel):

    response_extraction = CharField(max_length=252, null=True, verbose_name="临时提取变量")