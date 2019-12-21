class Response(object):

    """ 自定义异常 """
    """ 这里是通用异常 10000 ~ 10999 """
    error_1001 = '无效TOKEN，请重新登陆'
    error_1002 = 'WARNING: TOKEN NOT FOUND!'
    error_1003 = '该请求已经废弃'
    error_10001 = '参数错误'
    error_10002 = '操作失败'

    def __init__(self, code=None, msg=None, data=None):
        self.code = code
        self.msg = msg
        self.data = data

    def json(self):

        attr = 'error_{code}'.format(code=self.code)
        if hasattr(self, attr):
            msg = self.__getattribute__(attr)
        else:
            msg = self.msg

        return {
            "code": self.code,
            "msg": msg,
            "data": self.data
        }
