import ast
import json
import sys
from abc import ABC
import redis
import http.client as httplib
from tornado.web import RequestHandler, HTTPError
from apps.utils.logger import logger
from apps.utils.json_serializer import json_serializer


def log_response(handler):
    """
    记录服务器响应日志
    """

    content_type = handler._headers.get('Content-Type', None)
    # headers_str = handler. _convert_header_value(content_type)
    block = 'Response Infomations:\n' + _format_headers_log({'Content-Type': content_type})

    if content_type and ('text' in content_type or 'json' in content_type):
        limit = 0

        def cut(s):
            if limit and len(s) > limit:
                return [s[:limit]] + cut(s[limit:])
            else:
                return [s]

        try:
            body = handler._write_buffer[0].decode('utf-8')
        except Exception as e:
            body = f"{handler.__class__.__name__} object has {e}"

        lines = []
        for i in body.split('\n'):
            lines += ['| ' + j for j in cut(i)]
        block += '\nBody:\n' + '\n'.join(lines)

    logger.info(block.encode('gbk', 'ignore').decode('gbk'))


def log_request(handler):
    """
    记录服务器请求
    """
    block = 'Request Infomations:\n' + _format_headers_log(handler.request.headers)

    try:
        request_body = ast.literal_eval(handler.request.body.decode('utf-8'))
    except SyntaxError:
        request_body = handler.request.arguments

    if request_body:
        block += '+----Arguments----+\n'
        for k, v in request_body.items():
            block += '| {0:<15} | {1:<15} \n'.format(repr(k), repr(v))

    logger.info(block)


def _format_headers_log(headers):
    # length of '+-...-+' is 19
    block = '+-----Headers-----+\n'
    for k, v in headers.items():
        try:
            block += '| {0:<15} | {1:<15} \n'.format(k, v)
        except TypeError:
            block += '| {0:<15} | {1:<15} \n'.format('Undefined', 'Undefined')
    return block


class RedisHandler(RequestHandler, ABC):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis(**self.settings['redis'])


class BaseHandler(RequestHandler, ABC):

    EXCEPTION_HANDLERS = None

    PREPARES = []

    def _exception_default_handler(self, e):
        """重写tornado.web.RequestHandler._handle_request_exception
        """
        if isinstance(e, HTTPError):
            if e.log_message:
                format_msg = "%d %s: " + e.log_message
                args = [e.status_code, self._request_summary()] + list(e.args)
                logger.warning(format_msg, *args)
            if e.status_code not in httplib.responses:
                logger.error("Bad HTTP status code: %d", e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            logger.error("Uncaught exception %s\n%r", self._request_summary(),
                         self.request, exc_info=True)
            self.send_error(500, exc_info=sys.exc_info())

    def _handle_request_exception(self, e):
        """
        处理HTTPError异常，保留其他异常由用户定义的处理函数处理 映射到类属性“ EXCEPTION_HANDLERS”

        Common HTTP status codes:
            200 OK
            301 Moved Permanently
            302 Found
            400 Bad Request
            401 Unauthorized
            403 Forbidden
            404 Not Found
            405 Method Not Allowed
            500 Internal Server Error

        """
        handle_func = self._exception_default_handler
        if self.EXCEPTION_HANDLERS:
            for excs, func_name in self.EXCEPTION_HANDLERS.items():
                if isinstance(e, excs):
                    handle_func = getattr(self, func_name)
                    break

        handle_func(e)
        if not self._finished:
            self.finish()

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PATCH')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Authorization, tsessionid, Access-Control-Allow-Origin,'
                        ' Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def json(self, result):
        self.write(json.dumps(result, default=json_serializer, indent=4, ensure_ascii=False))
        self.finish()

    def options(self, *args, **kwargs):
        pass

    def prepare(self):
        """重写prepare中间件, 在`get`/`post`/etc请求之前调用
        """
        log_request(self)

        for i in self.PREPARES:
            getattr(self, 'prepare_' + i)()
            if self._finished:
                return

    def flush(self, *args, **kwargs):
        """
        在调用RequestHandler.flush之前，获得了_write_buffer
        """
        log_response(self)
        super(BaseHandler, self).flush(*args, **kwargs)