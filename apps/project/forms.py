"""
    项目管理模块表单验证器
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class ProjectForm(Form):

    name = StringField("项目名称", validators=[DataRequired("请输入项目名称")])
    env = IntegerField("测试环境", validators=[DataRequired("请选择环境")])
    desc = TextAreaField("项目描述", validators=[DataRequired(message="请输入项目描述")])


class TestEnvironmentForm(Form):

    name = StringField("测试环境名称", validators=[DataRequired("请输入测试环境名称")])
    host_address = StringField("测试环境地址", validators=[DataRequired("请输入测试环境地址")])
    desc = TextAreaField("测试环境描述", validators=[DataRequired(message="请输入测试环境描述")])


class DBSettingForm(Form):

    name = StringField("数据库名称", validators=[DataRequired("请输入数据库名称")])
    db_type = StringField("数据库类型", validators=[DataRequired("请输入数据库类型")])
    db_user = StringField("数据库账号", validators=[DataRequired("请输入数据库账号")])
    db_password = StringField("数据库密码", validators=[DataRequired("请输入数据库密码")])
    db_host = StringField("数据库境地址", validators=[DataRequired("请输入数据库地址")])
    db_port = IntegerField("数据库端口号", validators=[DataRequired("请输入数据库端口号")])
    desc = TextAreaField("数据库描述", validators=[DataRequired(message="请输入数据库描述")])


class FunctionGeneratorForm(Form):

    name = StringField("函数名称", validators=[DataRequired("请输入函数名称")])
    function = StringField("函数方法", validators=[DataRequired("请输入方法名称")])
    desc = TextAreaField("方法描述", validators=[DataRequired(message="请输入方法描述")])


class FunctionDebugForm(Form):
    function = StringField("函数方法", validators=[DataRequired("请输入方法名称")])
