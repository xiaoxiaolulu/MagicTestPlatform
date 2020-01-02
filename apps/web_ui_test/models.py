"""
    web Ui 测试模块数据库模型
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


class PageElement(BaseModel):

    element_name = CharField(max_length=50, null=True, verbose_name='元素名称')
    operate_type = CharField(max_length=50, null=True, verbose_name='操作方式')
    owner_page = CharField(max_length=50, null=True, verbose_name='所属页面')
    creator = ForeignKeyField(User, verbose_name="创建者")
    desc = TextField(verbose_name="元素描述")

    @classmethod
    def extend(cls):
        return cls.select(
            cls,
            User.id,
            User.nick_name) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator)
