from tornado.web import url
from apps.communities.handlers import GroupHandler, GroupMemberHandler


urlpatterns = [
    url('/groups/', GroupHandler),
    url('/groups/([0-9]+)/member', GroupMemberHandler)
]
