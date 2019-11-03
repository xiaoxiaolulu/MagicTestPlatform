from tornado.web import url, StaticFileHandler
from MagicTestPlatform.settings import settings
from apps.users.urls import urlpatterns as users_urls
from apps.communities.urls import urlpatterns as communities_urls
from apps.project.urls import urlpatterns as project_urls


urlpatterns = [
    url('/media/(.*)', StaticFileHandler, {'path': settings['MEDIA_ROOT']})
]

urlpatterns += users_urls
urlpatterns += communities_urls
urlpatterns += project_urls

