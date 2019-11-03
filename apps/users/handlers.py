import json
from abc import ABC
from random import choice
from datetime import datetime
import jwt
from apps.users.models import User
from apps.utils.Result import Result
from MagicTestPlatform.handlers import RedisHandler, BaseHandler
from apps.users.forms import SmsCodeForm, RegisterForm, LoginForm, RestPasswordForm


class SmsHandler(BaseHandler, RedisHandler, ABC):

    @staticmethod
    def generate_code():
        """
        生成随机4位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = SmsCodeForm.from_json(param)
        account = form.account.data

        if account is None:
            return self.json(
                Result(code=10080, msg='参数有误，缺少account参数!'))

        if form.validate():
            code = self.generate_code()
            self.redis_conn.set(f'{account}_{code}', 1, 10 * 60)
            return self.json(
                Result(code=1, msg="验证码已发送，请注意接收〜", data={'account': account, 'VerCode': code}))
        else:
            return self.json(Result(code=10090, msg=form.errors))


class RegisterHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = RegisterForm.from_json(param)
        account = form.account.data
        code = form.code.data
        password = form.password.data

        if account is None:
            return self.json(
                Result(code=10080, msg="参数有误, 不可缺少account参数"))
        if code is None:
            return self.json(
                Result(code=10080, msg="参数有误, 不可缺少code参数"))
        if password is None:
            return self.json(
                Result(code=10080, msg="参数有误, 不可缺少password参数"))

        if form.validate():
            if not self.redis_conn.get(f'{account}_{code}'):
                return self.json(
                    Result(code=10018, msg="验证码失效或不正确！"))

            else:
                try:
                    existed_user = await self.application.objects.get(User, account=account)
                    return self.json(
                        Result(code=10020, msg='这个账号已经被注册！'))

                # 没有创建user表
                except User.DoesNotExist:
                    user = await self.application.objects.create(User, account=account, password=password)
                    return self.json(
                        Result(code=1, msg='账号注册成功', data={'id': user.id}))
        else:
            return self.json(Result(code=10090, msg=form.errors))


class LoginHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = LoginForm.from_json(param)
        account = form.account.data
        password = form.password.data

        if account is None:
            return self.json(
                Result(code=10080, msg="参数有误, 不可缺少account字段")
            )

        if password is None:
            return self.json(
                Result(code=10080, msg="参数有误, 不可缺少password字段")
            )

        if form.validate():

            try:
                user = await self.application.objects.get(User, account=account)
                if not user.password.check_password(password):
                    return self.json(
                        Result(code=10090, msg="密码错误,请重新输入!")
                    )
                else:
                    payload = {
                        "id": user.id,
                        "nick_name": user.nick_name,
                        "exp": datetime.utcnow()
                    }
                    token = jwt.encode(
                        payload, self.settings['secret_key'], algorithm='HS256')

                    nick_name = user.nick_name if user.nick_name is not None else user.account
                    return self.json(
                        Result(
                            code=1, msg="登陆成功",
                            data={
                                'id': user.id,
                                'nick_name': nick_name,
                                'token': token.decode('utf-8')}))

            except User.DoesNotExist:
                return self.json(
                    Result(code=10020, msg="该账户不存在，尚未注册过！")
                )
        else:
            return self.json(
                Result(code=10090, msg="账号或密码错误, 请检查!")
            )


class RestPasswordHandler(BaseHandler, RedisHandler, ABC):

    async def post(self, *args, **kwargs):
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = RestPasswordForm.from_json(param)
        account = form.account.data
        password = form.password.data

        if account is None:
            self.json(
                Result(code=10080, msg="参数有误, 不可缺少account参数.")
            )

        if password is None:
            self.json(
                Result(code=10080, msg="参数有误, 不可缺少password参数.")
            )

        if form.validate():

            try:
                user = await self.application.objects.get(User, account=account)
                await self.application.objects.execute(User.update(password=password).where(User.account == account))
                return self.json(Result(code=1, msg="修改密码成功！"))
            except User.DoesNotExist:
                return self.json(
                    Result(code=10090, msg="该账号尚未被注册!")
                )
        else:
            return self.json(Result(code=10090, msg=form.errors))
