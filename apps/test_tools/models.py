"""
    测试工具模块数据库模型
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from peewee import *
from peewee import CharField
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


class ImageIdentifyText(BaseModel):

    image_name = CharField(max_length=50, null=True, verbose_name='图片名称')
    address = CharField(max_length=150, null=True, verbose_name="图片地址")
    content = TextField(verbose_name='图片文字')
    creator = ForeignKeyField(User, verbose_name="创建者")
    desc = TextField(verbose_name="图片描述")

    @classmethod
    def extend(cls):
        return cls.select(
            cls,
            User.id,
            User.nick_name) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator)
