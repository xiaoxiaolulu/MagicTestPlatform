

class CustomException(Exception):
    """ 自定义异常
    这里是通用异常 10000 ~ 21901
    """

    def __init__(self, code=None, desc=None, data=None):
        self.code = code
        self.desc = desc
        self.data = data

    @property
    def msg(self):
        if self.desc is not None:
            return self.desc

        attr = f'{"code": {self.code}, "msg": {self.desc}, "data": {self.data}}'
        if hasattr(self, attr):
            return self.__getattribute__(attr)
        else:
            return '未知异常'


class RequestContextError(CustomException):
    
    pass
