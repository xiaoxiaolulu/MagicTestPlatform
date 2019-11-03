from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, AnyOf
from wtforms_tornado import Form


class CommunityGroupForm(Form):

    name = StringField("名称", validators=[DataRequired("请输入小组名称")])
    category = StringField("类别", validators=[DataRequired("请输入小组名称"), AnyOf(
        values=['在线教育', '同城交易', '哲学思辨', '史海钩沉', '天文地理'])])
    desc = TextAreaField("简介", validators=[DataRequired(message="请输入简介")])
    notice = TextAreaField("公告", validators=[DataRequired(message="请输入公告")])


class GroupApplyForm(Form):

    apply_reason = StringField("申请理由", validators=[DataRequired("请输入申请理由")])
