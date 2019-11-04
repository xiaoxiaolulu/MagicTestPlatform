from tornado.web import url
from apps.project.handlers import (
    ProjectHandler, ProjectChangeHandler, TestEnvironmentHandler, TestEnvironmentChangeHandler, )

urlpatterns = [
    url('/projects/', ProjectHandler),
    url("/projects/([0-9]+)/", ProjectChangeHandler),
    url('/test_env/', TestEnvironmentHandler),
    url("/test_env/([0-9]+)/", TestEnvironmentChangeHandler),
]