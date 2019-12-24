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

READ_DOT_ENV_FILE = env.bool("TORNADO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    env.read_env(str(BASE_DIR.path(".env")))


#################
#   调式开关     #
#################
DEBUG = env.bool("TORNADO_DEBUG", False)


#################
#   日志配置     #
#################
LOG_PATH = str(BASE_DIR.path('./logs'))
LOG_BACKUP_NUM = env.int('BACKUP_NUM', default=5)


#################
#   全局配置     #
#################
TORNADO_CONF = {
    'SITE_URL': "http://127.0.0.1:8082",
    'static_path': str(BASE_DIR.path('./statics')),
    'MEDIA_ROOT': str(BASE_DIR.path('./media')),
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
    'default': env.dict('REDIS', default={'host': '127.0.0.1', 'port': 6379})
}


#################
#  调式环境配置   #
#################
CODE_DEBUG = env.db("SERVER_URL", default="server://root:bubai.4393,@172.81.242.70:22")


#################
#  百度AI Toekn  #
#################
BAIDUCE_AUTH = r'https://aip.baidubce.com/oauth/2.0/token?' \
               r'grant_type=client_credentials&client_id=' \
               r'fDowQhVGrfyof0oFlNAowVTY&client_secret=YegBNDm1gHoXwyEBwxOsNr8WoFMzqmVS'


#################
# 百度图像识别    #
#################
BAIDUCE_API = r"https://aip.baidubce.com/rest/2.0/ocr/v1/general"


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
