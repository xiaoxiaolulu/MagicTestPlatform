from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, AnyOf
from wtforms_tornado import Form


class ProjectForm(Form):

    name = StringField("项目名称", validators=[DataRequired("请输入项目名称")])
    desc = TextAreaField("项目描述", validators=[DataRequired(message="请输入项目描述")])
