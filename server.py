import wtforms_json
from peewee_async import Manager
from tornado import web, ioloop
from MagicTestPlatform.settings import settings, database
from apps.utils.Router import route


def make_app():
    # 创建app，并且把路有关系放入到Application对象中
    return web.Application(route.urls, debug=True, **settings)


if __name__ == '__main__':
    app = make_app()
    wtforms_json.init()
    app.listen(8082)
    objects = Manager(database)
    database.set_allow_sync(False)
    app.objects = objects
    ioloop.IOLoop.current().start()
