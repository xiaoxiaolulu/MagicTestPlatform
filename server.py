import wtforms_json
from peewee_async import Manager
from tornado import web, ioloop
from MagicTestPlatform.settings import settings, database
from apps.utils.Router import route
from apps.project.handlers import *
from apps.users.handlers import *


def make_app():
    # 创建app，并且把路有关系放入到Application对象中
    return web.Application(route.urls, debug=True, **settings)


def main():
    app = make_app()
    wtforms_json.init()
    app.listen(9098)
    objects = Manager(database)
    database.set_allow_sync(False)
    app.objects = objects
    ioloop.IOLoop.current().start()
    return app


if __name__ == '__main__':
    main()
