"""
    �ӿڲ���ģ�����֤��
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from wtforms_tornado import Form


class InterfacesForm(Form):

    interface_name = StringField("�ӿ�����", validators=[DataRequired("������ӿ�����")])
    url = StringField("�����ַ", validators=[DataRequired("�����������ַ")])
    method = StringField("���󷽷�", validators=[DataRequired("���������󷽷�")])
    headers = StringField("����ͷ��", validators=[DataRequired("����ͷ��")])
    params = StringField("�������", validators=[DataRequired("�������")])
    project = IntegerField("��Ŀ����", validators=[DataRequired("��ѡ����Ŀ")])
    desc = TextAreaField("��������", validators=[DataRequired(message="�����뷽������")])

