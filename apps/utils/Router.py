

class Route(object):
    """ 把每个URL与Handler的关系保存到一个元组中，然后追加到列表内，列表内包含了所有的Handler """

    def __init__(self):
        # 路由列表
        self.urls = list()

    def __call__(self, url, *args, **kwargs):
        def register(cls):
            # 把路由的对应关系表添加到路由列表中
            self.urls.append((url, cls))
            return cls

        return register


route = Route()
