import ast
import json
import sys
import response
from abc import ABC
import redis
from torext.log import app_log
from tornado.web import RequestHandler, HTTPError
from apps.utils.json_serializer import json_serializer
from torext.compat import httplib


def log_response(handler):
    """
    Acturally, logging response is not a server's responsibility,
    you should use http tools like Chrome Developer Tools to analyse the response.

    Although this function and its setting(LOG_RESPONSE) is not recommended to use,
    if you are laze as I was and working in development, nothing could stop you.
    """
    content_type = handler._headers.get('Content-Type', None).decode('utf-8')
    headers_str = handler._generate_headers()
    block = 'Response Infomations:\n' + headers_str.strip().decode('utf-8')

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
    app_log.info(block)


def log_request(handler):
    """
    Logging request is opposite to response, sometime its necessary,
    feel free to enable it.
    """
    block = 'Request Infomations:\n' + _format_headers_log(handler.request.headers)

    request_body = ast.literal_eval(handler.request.body.decode('utf-8'))

    if request_body:
        block += '+----Arguments----+\n'
        for k, v in request_body.items():
            block += '| {0:<15} | {1:<15} \n'.format(repr(k), repr(v))

    app_log.info(block)


def _format_headers_log(headers):
    # length of '+-...-+' is 19
    block = '+-----Headers-----+\n'
    for k, v in headers.items():
        block += '| {0:<15} | {1:<15} \n'.format(k, v)
    return block


class RedisHandler(RequestHandler, ABC):

    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.redis_conn = redis.StrictRedis(**self.settings['redis'])


class BaseHandler(RequestHandler, ABC):

    EXCEPTION_HANDLERS = None

    PREPARES = []

    def _exception_default_handler(self, e):
        """This method is a copy of tornado.web.RequestHandler._handle_request_exception
        """
        if isinstance(e, HTTPError):
            if e.log_message:
                format = "%d %s: " + e.log_message
                args = [e.status_code, self._request_summary()] + list(e.args)
                app_log.warning(format, *args)
            if e.status_code not in httplib.responses:
                app_log.error("Bad HTTP status code: %d", e.status_code)
                self.send_error(500, exc_info=sys.exc_info())
            else:
                self.send_error(e.status_code, exc_info=sys.exc_info())
        else:
            app_log.error("Uncaught exception %s\n%r", self._request_summary(),
                          self.request, exc_info=True)
            self.send_error(500, exc_info=sys.exc_info())

    def _handle_request_exception(self, e):
        """This method handle HTTPError exceptions the same as how tornado does,
        leave other exceptions to be handled by user defined handler function
        maped in class attribute `EXCEPTION_HANDLERS`

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

        It is suggested only to use above HTTP status codes
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
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, DELETE, PUT, PATCH, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Authorization, tsessionid, Access-Control-Allow-Origin,'
                        ' Access-Control-Allow-Headers, X-Requested-By, Access-Control-Allow-Methods')

    def json(self, result):
        self.write(json.dumps(result, default=json_serializer, indent=4, ensure_ascii=False))
        self.finish()

    def options(self, *args, **kwargs):
        pass

    def prepare(self):
        """Behaves like a middleware between raw request and handling process,

        If `PREPARES` is defined on handler class, which should be
        a list, for example, ['auth', 'context'], method whose name
        is constitute by prefix '_prepare_' and string in this list
        will be executed by sequence. In this example, those methods are
        `_prepare_auth` and `_prepare_context`
        """
        log_request(self)

        for i in self.PREPARES:
            getattr(self, 'prepare_' + i)()
            if self._finished:
                return

    def flush(self, *args, **kwgs):
        """
        Before `RequestHandler.flush` was called, we got the final _write_buffer.

        This method will not be called in wsgi mode
        """
        log_response(self)
        super(BaseHandler, self).flush(*args, **kwgs)