from tornado.util import import_object
from common.storage import storage


class Settings(object):

    def __init__(self):
        pass

    def get_settings(self, name):
        """

        :param name: 配置名
        :return:配置项
        """
        global_settings = import_object('settings.base')
        self._config = global_settings

        if hasattr(self._config, name):
            return getattr(self._config, name)
        elif hasattr(self._config, name):
            return getattr(self._config, name)
        else:
            raise Exception('config "%s" not exist!' % name)

    def __getattr__(self, item):
        setting = self.get_settings(item)
        return storage(setting) if type(setting) is dict else setting


settings = Settings()
