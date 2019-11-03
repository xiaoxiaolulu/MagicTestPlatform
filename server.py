from peewee_async import Manager
from tornado import web, ioloop
from MagicTestPlatform.urls import urlpatterns
from MagicTestPlatform.settings import settings, database

if __name__ == '__main__':
    import wtforms_json
    wtforms_json.init()
    app = web.Application(urlpatterns, debug=True, **settings)
    app.listen(8082)
    objects = Manager(database)
    database.set_allow_sync(False)
    app.objects = objects
    ioloop.IOLoop.current().start()
