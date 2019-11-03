from datetime import datetime
from peewee import *
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


class CommunityGroup(BaseModel):

    creator = ForeignKeyField(User, verbose_name="创建者")
    name = CharField(max_length=100, null=True, verbose_name="名称")
    category = CharField(max_length=20, verbose_name="分类", null=True)
    cover = CharField(max_length=200, null=True, verbose_name="封面图")
    desc = TextField(verbose_name="简介")
    notice = TextField(verbose_name="公告")
    member_nums = IntegerField(default=0, verbose_name="成员数")
    post_nums = IntegerField(default=0, verbose_name="帖子数")

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)


HANDLE_STATUS = {
    ('agree', '同意'),
    ('refuse', '拒绝')
}


class CommunityGroupMember(BaseModel):

    user = ForeignKeyField(User, verbose_name="用户")
    community = ForeignKeyField(CommunityGroup, verbose_name="小组")
    status = CharField(choices=HANDLE_STATUS, max_length=10, null=True, verbose_name="处理状态")
    handler_msg = CharField(max_length=200, null=True, verbose_name="处理内容")
    apply_reason = CharField(max_length=200, verbose_name="申请理由")
    handler_time = DateTimeField(default=datetime.now(), verbose_name="加入时间")
