from peewee import *
from bcrypt import (
    hashpw,
    gensalt
)
from MagicTestPlatform.models import BaseModel


class PasswordHash(bytes):
    
    def check_password(self, password):
        password = password.encode('utf-8')
        return hashpw(password, self) == self
    

class PasswordField(BlobField):
    
    def __init__(self, iterations=12, *args, **kwargs):
        if None in (hashpw, gensalt):
            raise ValueError('Missing library required for PasswordField: bcrypt')
        self.bcrypt_iterations = iterations
        self.raw_password = None
        super(PasswordField, self).__init__(*args, **kwargs)
    
    def db_value(self, value):
        if isinstance(value, PasswordHash):
            return bytes(value)
    
        if isinstance(value, str):
            value = value.encode('utf-8')
        salt = gensalt(self.bcrypt_iterations)
        return value if value is None else hashpw(value, salt)
    
    def python_value(self, value):
        if isinstance(value, str):
            value = value.encode('utf-8')
        
        return PasswordHash(value)
    

GENDERS = (
    ('female', '女'),
    ('male', '男')
)


class User(BaseModel):

    account = CharField(max_length=30, verbose_name='账号', index=True, unique=True)
    password = PasswordField(verbose_name='密码')
    nick_name = CharField(max_length=20, null=True, verbose_name='昵称')
    head_url = CharField(max_length=200, null=True, verbose_name='头像')
    address = CharField(max_length=200, null=True, verbose_name='地址')
    desc = TextField(null=True, verbose_name='个人简介')
    gender = CharField(max_length=200, choices=GENDERS, null=True, verbose_name='性别')
