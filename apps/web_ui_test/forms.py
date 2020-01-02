"""
    web Ui测试模块表单验证器
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from wtforms import (
    StringField,
    IntegerField,
    FieldList
)
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class PageElementForm(Form):

    element_name = StringField("元素名称", validators=[DataRequired("请输入元素名称")])
    operate_type = StringField("操作方法", validators=[DataRequired("请输入操作方法")])
    owner_page = StringField("所属页面", validators=[DataRequired("请输入所属页面")])
    desc = StringField("元素描述", validators=[DataRequired("请输入元素描述")])
