import json
from abc import ABC
from datetime import datetime
import jwt
from apps.users.models import User
from MagicTestPlatform.handlers import (
    RedisHandler,
    BaseHandler
)
from apps.users.forms import (
    SmsCodeForm,
    RegisterForm,
    LoginForm,
    PasswordForm
)
from common.core import (
    route,
    generate_code
)
from common.parse_settings import settings
from common.validator import JsonResponse


@route(r'/code/')
class SmsHandler(BaseHandler, RedisHandler, ABC):

    def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = SmsCodeForm.from_json(param)
        account = form.account.data

        if form.validate():
            code = generate_code()
            self.redis_conn.set(f'{account}_{code}', 1, 10 * 60)
            return self.json(
                JsonResponse(code=1, data={'account': account, 'VerCode': code}))
        else:
            self.set_status(404)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/register/')
class RegisterHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = RegisterForm.from_json(param)
        account = form.account.data
        code = form.code.data
        password = form.password.data

        if form.validate():
            if not self.redis_conn.get(f'{account}_{code}'):
                self.set_status(400)
                return self.json(JsonResponse(code=10006))

            else:
                try:
                    await self.application.objects.get(User, account=account)
                    self.set_status(400)
                    return self.json(JsonResponse(code=10007))

                except User.DoesNotExist:
                    user = await self.application.objects.create(User, account=account, password=password)
                    return self.json(
                        JsonResponse(code=1, data={'id': user.id}))
        else:
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/login/')
class LoginHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = LoginForm.from_json(param)
        account = form.account.data
        password = form.password.data

        if form.validate():

            try:
                user = await self.application.objects.get(User, account=account)
                if not user.password.check_password(password):
                    return self.json(JsonResponse(code=10008))

                else:
                    payload = {
                        "id": user.id,
                        "nick_name": user.nick_name,
                        "exp": datetime.utcnow()
                    }
                    token = jwt.encode(
                        payload,
                        settings.TORNADO_CONF.secret_key, algorithm='HS256'
                    )

                    nick_name = user.nick_name if user.nick_name is not None else user.account
                    return self.json(
                        JsonResponse(
                            code=1,
                            data={
                                'id': user.id,
                                'nick_name': nick_name,
                                'token': token.decode('utf-8')})
                    )

            except User.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))
        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10008))


@route(r'/rest/')
class RestPasswordHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = PasswordForm.from_json(param)

        if form.validate():
            # 检查旧密码
            if not self.current_user.password.check_password(form.oldPassword.data):
                self.set_status(400)
                self.json(JsonResponse(code=10008))
            else:
                if form.newPassword.data != form.checkPassword.data:
                    self.set_status(400)
                    self.json(JsonResponse(code=10008))
                else:
                    self.current_user.password = form.newPassword.data
                    await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))
