"""
    测试工具模块表单验证器
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


class ImageIdentifyTextForm(Form):

    image_name = StringField("图片名称", validators=[DataRequired("请输入图片名称")])
    desc = StringField("图片描述", validators=[DataRequired("请输入图片描述")])
