import os
import peewee_async

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = {
    'SITE_URL': "http://127.0.0.1:8082",
    'static_path': os.path.join(BASE_DIR, 'statics'),
    'MEDIA_ROOT': os.path.join(BASE_DIR, 'media'),
    'static_url_prefix': '/statics/',
    'template_path': 'templates',
    "secret_key": "ZGGA#SJHKS$S6Si",
    "jwt_expire": 7*24*3600,
    'db': {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '123456',
        'name': 'lehuforum',
        'port': 3306
    },
    'redis': {
        'host': '127.0.0.1',
        'port': 6379
    }
}


database = peewee_async.MySQLDatabase(
    database=settings['db']['name'], host=settings['db']['host'], port=settings['db']['port'], user=settings['db']['user'],
    password=settings['db']['password']
)
