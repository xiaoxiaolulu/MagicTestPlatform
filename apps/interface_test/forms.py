"""
    接口测试模块表单验证器
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class InterfacesDebugForm(Form):

    interface_name = StringField("接口名称", validators=[DataRequired("请输入接口名称")])
    url = StringField("请求地址", validators=[DataRequired("请输入请求地址")])
    method = StringField("请求方法", validators=[DataRequired("请输入请求方法")])
    headers = StringField("请求头部", validators=[DataRequired("请输入请求头部")])
    params = StringField("请求参数", validators=[DataRequired("请输入请求参数")])
    project = IntegerField("项目配置", validators=[DataRequired("请选择项目")])
