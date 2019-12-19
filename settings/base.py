"""
项目全局配置文件
"""
import environ
import peewee_async


#################
#   全局路径     #
#################
BASE_DIR = (
        environ.Path(__file__) - 2
)

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("TORNADO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env(str(BASE_DIR.path(".env")))


#################
#   调式开关     #
#################
DEBUG = env.bool("TORNADO_DEBUG", False)


#################
#   日志路径     #
#################
LOG_PATH = BASE_DIR.path('./logs')


#################
#   全局配置     #
#################
TORNADO_CONF = {
    'SITE_URL': "http://127.0.0.1:8082",
    'static_path': BASE_DIR.path('./statics'),
    'MEDIA_ROOT': BASE_DIR.path('./media'),
    'static_url_prefix': '/statics/',
    'template_path': 'templates',
    "secret_key": "ZGGA#SJHKS$S6Si",
    "jwt_expire": 7 * 24 * 3600,
}


#################
#   数据库配置    #
#################
DATABASES = env.db("DATABASE_URL", default="mysql://root:123456@127.0.0.1:3306/magic")


#################
#   Redis配置    #
#################
REDIS = {
    'default': env.db('REDIS_URL', default="rediscache://127.0.0.1:6379")
}


#################
#  调式环境配置   #
#################
CODE_DEBUG = env.db("SERVER_URL", default="server://root:bubai.4393,@172.81.242.70:22")


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
