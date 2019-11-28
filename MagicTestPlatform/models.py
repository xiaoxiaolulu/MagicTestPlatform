from datetime import datetime
from peewee import *
from MagicTestPlatform.settings import database_async


class BaseModel(Model):

    add_time = DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        database = database_async
