from tornado.web import url
from apps.project.handlers import ProjectHandler, ProjectChangeHandler

urlpatterns = [
    url('/projects/', ProjectHandler),
    url("/projects/([0-9]+)/", ProjectChangeHandler),
]