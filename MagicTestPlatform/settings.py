"""
项目全局配置文件
"""
import os
import peewee_async

#################
#   全局路径     #
#################
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


#################
#   调式开关     #
#################
DEBUG = True


#################
#   全局配置     #
#################
TORNADO_CONF = {
    'SITE_URL': "http://127.0.0.1:8082",
    'static_path': os.path.join(BASE_DIR, 'statics'),
    'MEDIA_ROOT': os.path.join(BASE_DIR, 'media'),
    'static_url_prefix': '/statics/',
    'template_path': 'templates',
    "secret_key": "ZGGA#SJHKS$S6Si",
    "jwt_expire": 7 * 24 * 3600,
}


#################
#   数据库配置    #
#################
DATABASES = {
    'NAME': 'magic',
    'USER': 'root',
    'PASSWORD': '123456',
    'HOST': '127.0.0.1',
    'PORT': 3306
}


#################
#   Redis配置    #
#################
REDIS = {
    'default': {
        'host': '127.0.0.1',
        'port': 6379
    }
}


#################
# 数据库异步配置  #
#################
database = peewee_async.MySQLDatabase(
    database=DATABASES['NAME'],
    host=DATABASES['HOST'],
    port=DATABASES['PORT'],
    user=DATABASES['USER'],
    password=DATABASES['PASSWORD']
)
