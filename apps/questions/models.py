from peewee import  *
from MagicTestPlatform.models import BaseModel
from apps.users.models import User


class Question(BaseModel):

    user = ForeignKeyField(User, verbose_name="用户")
    category = CharField(max_length=200, verbose_name="分类", null=True)
    title = CharField(max_length=200, verbose_name="标题", null=True)
    content = TextField(verbose_name='内容')
    image = CharField(default=255, verbose_name='图片')
    answer_nums = IntegerField(default=0, verbose_name='回答数')

    @classmethod
    def extend(cls):
        return cls.select(cls, User.id, User.nick_name).join(User)


class Answer(BaseModel):

    user = ForeignKeyField(User, verbose_name="用户", related_name="author")
    question = ForeignKeyField(Question, verbose_name="问题")
    parent_answer = ForeignKeyField('self', null=True, verbose_name="回答", related_name='answer_parent')
    reply_user = ForeignKeyField(User, verbose_name="用户", related_name='replay_author', null=True)
    content = TextField(verbose_name='内容')
    replay_nums = IntegerField(default=0, verbose_name='回复数')
    
    @classmethod
    def extend(cls):
        author = User.alias()
        relyed_user = User.alias()
        return