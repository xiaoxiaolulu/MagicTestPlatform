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
    Response,
    route,
    generate_code
)
from common.parse_settings import settings


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
                Response(code=1, msg="验证码已发送，请注意接收〜", data={'account': account, 'VerCode': code}))
        else:
            self.set_status(404)
            return self.json(Response(code=10090, msg=form.errors))


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
                return self.json(Response(code=10018, msg="验证码失效或不正确！"))

            else:
                try:
                    await self.application.objects.get(User, account=account)
                    self.set_status(400)
                    return self.json(Response(code=10020, msg='这个账号已经被注册！'))

                except User.DoesNotExist:
                    user = await self.application.objects.create(User, account=account, password=password)
                    return self.json(
                        Response(code=1, msg='账号注册成功', data={'id': user.id}))
        else:
            return self.json(Response(code=10090, msg=form.errors))


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
                    return self.json(Response(code=10090, msg="密码错误,请重新输入!"))

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
                        Response(
                            code=1, msg="登陆成功",
                            data={
                                'id': user.id,
                                'nick_name': nick_name,
                                'token': token.decode('utf-8')}))

            except User.DoesNotExist:
                self.set_status(400)
                return self.json(Response(code=10020, msg="该账户不存在，尚未注册过！"))
        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg="账号或密码错误, 请检查!"))


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
                self.json(Response(code=10090, msg="旧密码错误!"))
            else:
                if form.newPassword.data != form.checkPassword.data:
                    self.set_status(400)
                    self.json(Response(code=10090, msg="两次密码不一致!"))
                else:
                    self.current_user.password = form.newPassword.data
                    await self.application.objects.update(self.current_user)
        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))
