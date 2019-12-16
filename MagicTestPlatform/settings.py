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
#   日志路径     #
#################
LOG_PATH = os.path.join(BASE_DIR, 'logs')


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
#  调式环境配置   #
#################
CODE_DEBUG = {
    'HOST': '172.81.242.70',
    'PORT': 22,
    'USER': 'root',
    'PASSWORD': 'bubai.4393,'
}


#################
# 数据库异步配置  #
#################
database_async = peewee_async.MySQLDatabase(
    database=DATABASES.get('NAME'),
    host=DATABASES.get('HOST'),
    port=DATABASES.get('PORT'),
    user=DATABASES.get('USER'),
    password=DATABASES.get('PASSWORD')
)
