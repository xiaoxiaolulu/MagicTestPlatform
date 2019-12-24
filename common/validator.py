class JsonResponse(object):

    """ 通用code码 10000 ~ 10999 """
    code_1 = "success"
    code_10001 = '无效TOKEN，请重新登陆'
    code_10002 = 'WARNING: TOKEN NOT FOUND!'
    code_10003 = '该请求已经废弃'
    code_10004 = '参数错误'
    code_10005 = '操作失败'
    code_10006 = '验证码失效或不正确!'
    code_10007 = '数据已存在'
    code_10008 = '参数错误, 请检查'
    code_10009 = '数据尚未创建'

    def __init__(self, code=None, msg=None, data=None):
        self.code = code
        self.msg = msg
        self.data = data

        if self.msg is None:

            attr = 'code_{code}'.format(code=self.code)

            if hasattr(self, attr):
                self.msg = self.__getattribute__(attr)
