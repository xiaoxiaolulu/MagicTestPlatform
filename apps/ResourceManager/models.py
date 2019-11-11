from datetime import datetime

from peewee import *
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


PHONE_STATUS = {
    ('idle', '闲置'),
    ('using', '使用中'),
    ('lent', '已借出')
}


class TestPhoneManager(BaseModel):

    user = ForeignKeyField(User, verbose_name="用户")
    status = CharField(choices=PHONE_STATUS, max_length=10, null=True, verbose_name="测试机状态")
    lent_user = CharField(max_length=20, verbose_name="借出人")
    lent_time = DateTimeField(default=datetime.now(), verbose_name="借出时间")
