from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, AnyOf
from wtforms_tornado import Form


class ProjectForm(Form):

    name = StringField("项目名称", validators=[DataRequired("请输入项目名称")])
    desc = TextAreaField("项目描述", validators=[DataRequired(message="请输入项目描述")])


class TestEnvironmentForm(Form):

    name = StringField("测试环境名称", validators=[DataRequired("请输入测试环境名称")])
    host_address = StringField("测试环境地址", validators=[DataRequired("请输入测试环境地址")])
    desc = TextAreaField("测试环境描述", validators=[DataRequired(message="请输入测试环境描述")])
