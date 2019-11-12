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

    def __init__(self, name: StringField = None, env: IntegerField = None, desc: TextAreaField = None, **kwargs):
        super().__init__(**kwargs)
        self.name: StringField = name
        self.env: IntegerField = env
        self.desc: TextAreaField = desc


class TestEnvironmentForm(Form):

    name = StringField("测试环境名称", validators=[DataRequired("请输入测试环境名称")])
    host_address = StringField("测试环境地址", validators=[DataRequired("请输入测试环境地址")])
    desc = TextAreaField("测试环境描述", validators=[DataRequired(message="请输入测试环境描述")])

    def __init__(self, name: StringField = None, host_address: StringField = None, desc: TextAreaField = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.name: StringField = name
        self.host_address: StringField = host_address
        self.desc: TextAreaField = desc


class DBSettingForm(Form):

    name = StringField("数据库名称", validators=[DataRequired("请输入数据库名称")])
    db_type = StringField("数据库类型", validators=[DataRequired("请输入数据库类型")])
    db_user = StringField("数据库账号", validators=[DataRequired("请输入数据库账号")])
    db_password = StringField("数据库密码", validators=[DataRequired("请输入数据库密码")])
    db_host = StringField("数据库境地址", validators=[DataRequired("请输入数据库地址")])
    db_port = IntegerField("数据库端口号", validators=[DataRequired("请输入数据库端口号")])
    desc = TextAreaField("数据库描述", validators=[DataRequired(message="请输入数据库描述")])

    def __init__(
            self,
            name: StringField = None,
            db_type: StringField = None,
            db_user: StringField = None,
            db_password: StringField = None,
            db_host: StringField = None,
            db_port: IntegerField = None,
            desc: TextAreaField = None,
            **kwargs):
        super().__init__(**kwargs)
        self.name: StringField = name
        self.db_type: StringField = db_type
        self.db_user: StringField = db_user
        self.db_password: StringField = db_password
        self.db_host: StringField = db_host
        self.db_port: IntegerField = db_port
        self.desc: TextAreaField = desc


class FunctionGeneratorForm(Form):

    name = StringField("函数名称", validators=[DataRequired("请输入函数名称")])
    function = StringField("函数方法", validators=[DataRequired("请输入方法名称")])
    desc = TextAreaField("方法描述", validators=[DataRequired(message="请输入方法描述")])

    def __init__(self, name: StringField = None, function: StringField = None, desc: TextAreaField = None, **kwargs):
        super().__init__(**kwargs)
        self.name: StringField = name
        self.function: StringField = function
        self.desc: TextAreaField = desc


class FunctionDebugForm(Form):
    function = StringField("函数方法", validators=[DataRequired("请输入方法名称")])

    def __init__(self, function: StringField = None, **kwargs):
        super().__init__(**kwargs)
        self.function: StringField = function
