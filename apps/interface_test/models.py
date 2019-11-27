"""
    �ӿڲ���ģ�����ݿ�ģ��
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

    """"
    �ӿ��������ݿ�ģ��
    """

    interface_name = CharField(max_length=50, null=True, verbose_name="�ӿ�����")
    url = CharField(max_length=252, null=True, verbose_name="����·��")
    method = CharField(max_length=25, null=True, verbose_name="����ʽ")
    headers = CharField(max_length=252, null=True, verbose_name="����ͷ��")
    params = CharField(max_length=252, null=True, verbose_name="�������")
    assertion = CharField(max_length=252, null=True, verbose_name="��������")
    db = ForeignKeyField(DBSetting, verbose_name="���ݿ�����")
    check_db = CharField(max_length=252, null=True, verbose_name="���У��")
    response_extraction = CharField(max_length=252, null=True, verbose_name="����ֵ��ȡ")
    creator = ForeignKeyField(User, verbose_name="������")
    project = ForeignKeyField(Project, verbose_name='��������')
    desc = TextField(verbose_name="�ӿ�����")

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
            Project.name,
            Project.env) \
            .join(User, join_type=JOIN.LEFT_OUTER, on=cls.creator).switch(cls) \
            .join(DBSetting, join_type=JOIN.LEFT_OUTER, on=cls.db).switch(cls) \
            .join(Project, join_type=JOIN.LEFT_OUTER, on=cls.project)
