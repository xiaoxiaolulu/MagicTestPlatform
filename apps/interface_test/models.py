"""
    接口测试模块数据库模型
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from peewee import *
from peewee import CharField
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


class VariableDependency(BaseModel):

    response_extraction = CharField(max_length=252, null=True, verbose_name="临时提取变量")