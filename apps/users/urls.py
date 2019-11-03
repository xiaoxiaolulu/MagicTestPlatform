from tornado.web import url
from apps.users.handlers import SmsHandler, RegisterHandler, LoginHandler, RestPasswordHandler

urlpatterns = [
    url('/code/', SmsHandler),
    url('/register/', RegisterHandler),
    url('/login/', LoginHandler),
    url('/rest/', RestPasswordHandler)
]
