import wtforms_json
from peewee_async import Manager
from tornado import web
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from MagicTestPlatform.settings import database_async
from apps.utils.parse_settings import settings
from apps.utils.Router import route


class Application(web.Application):
    def __init__(self):
        wtforms_json.init()
        objects = Manager(database_async)
        database_async.set_allow_sync(False)
        web.Application.objects = objects
        super(Application, self).__init__(route.urls, debug=settings.DEBUG, **settings.TORNADO_CONF)


def main():
    print("http server start, Ctrl + C to stop...")
    http_server = HTTPServer(Application(), xheaders=True)
    http_server.listen(8084)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
