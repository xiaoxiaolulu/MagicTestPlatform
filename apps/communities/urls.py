from tornado.web import url
from apps.communities.handlers import GroupHandler, GroupMemberHandler, PostDetailHandler, GroupDetailHandler, PostHandler


urlpatterns = [
    url('/groups/', GroupHandler),
    url('/groups/([0-9]+)', GroupDetailHandler),
    url('/groups/([0-9]+)/member', GroupMemberHandler),
    url('/groups/([0-9]+)/posts', PostHandler),
    url('/posts/([0-9]+)/', PostDetailHandler),
]
