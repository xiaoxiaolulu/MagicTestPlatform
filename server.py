import wtforms_json
from peewee_async import Manager
from tornado import web, ioloop
from MagicTestPlatform.urls import urlpatterns
from MagicTestPlatform.settings import settings, database

app = web.Application(urlpatterns, debug=True, **settings)


def main():
    wtforms_json.init()
    app.listen(8082)
    objects = Manager(database)
    database.set_allow_sync(False)
    app.objects = objects
    ioloop.IOLoop.current().start()
    return app


if __name__ == '__main__':
    main()
