from wtforms_tornado import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Regexp


EMAIL_REGEX = "^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$"


class SmsCodeForm(Form):

    account = StringField('账号', validators=[DataRequired(message='请输入账号'),
                                            Regexp(EMAIL_REGEX, message="请输入合法的账号")])


class RegisterForm(Form):

    account = StringField('账号', validators=[DataRequired(message='请输入账号'),
                                            Regexp(EMAIL_REGEX, message="请输入合法的账号")])
    code = StringField('验证码', validators=[DataRequired(message='请输入验证码')])
    password = StringField('密码', validators=[DataRequired(message='请输入密码')])


class LoginForm(Form):

    account = StringField('账号', validators=[DataRequired(message='请输入账号'),
                                            Regexp(EMAIL_REGEX, message="请输入合法的账号")])
    password = StringField('密码', validators=[DataRequired(message='请输入密码')])


class PasswordForm(Form):

    oldPassword = StringField("旧密码", validators=[DataRequired(message="请输入旧密码")])
    newPassword = StringField("新密码", validators=[DataRequired(message="请输入新密码")])
    checkPassword = StringField("确认密码", validators=[DataRequired(message="请输入确认密码")])
