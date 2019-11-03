import json
from abc import ABC
import redis
from tornado.web import RequestHandler

from apps.utils.json_serializer import json_serializer


class RedisHandler(RequestHandler, ABC):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis(**self.settings['redis'])


class BaseHandler(RequestHandler, ABC):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Authorization, tsessionid, Access-Control-Allow-Origin,'
                        ' Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def json(self, result):
        self.write(json.dumps(result, default=json_serializer, indent=4, ensure_ascii=False))
        self.finish()

    def options(self, *args, **kwargs):
        pass


