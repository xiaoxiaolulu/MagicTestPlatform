from tornado.web import url
from apps.project.handlers import (
    ProjectHandler, ProjectChangeHandler, TestEnvironmentHandler, TestEnvironmentChangeHandler,
    DbSettingHandler, DbSettingChangeHandler, FunctionDebugHandler, FunctionHandler, FunctionChangeHandler
)

urlpatterns = [
    url('/projects/', ProjectHandler),
    url("/projects/([0-9]+)/", ProjectChangeHandler),
    url('/test_envs/', TestEnvironmentHandler),
    url("/test_envs/([0-9]+)/", TestEnvironmentChangeHandler),
    url('/db_settings/', DbSettingHandler),
    url("/db_settings/([0-9]+)/", DbSettingChangeHandler),
    url("/debug/", FunctionDebugHandler),
    url('/functions/', FunctionHandler),
    url("/functions/([0-9]+)/", FunctionChangeHandler),
]
