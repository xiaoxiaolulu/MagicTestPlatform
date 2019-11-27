import ast
import json
from abc import ABC
from urllib import parse
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.interface_test.forms import InterfacesDebugForm
from apps.project.models import Project
from apps.utils import authenticated_async, Result, route
from apps.utils.Recursion import GetJsonParams
from apps.utils.http_keywords import BaseKeyWords


@route(r'/interfaces_debug/')
class InterfacesDebugHandler(BaseHandler, ABC):

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        当前接口调试运行
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = InterfacesDebugForm.from_json(param)

        if form.validate():

            name = form.interface_name.data
            api = form.url.data
            method = form.method.data
            headers = form.headers.data
            params = form.params.data
            project = form.project.data

            # 获取配置Host地址
            project_query = Project.extend().filter(Project.id == project)
            projects = await self.application.objects.execute(project_query)
            host = GetJsonParams.get_value(model_to_dict(projects[0]), 'host_address')

            if method in ['get', 'GET']:
                request_body = {
                    'url': getattr(parse, 'urljoin')(host, api),
                    'method': method,
                    'params': params,
                    'headers': ast.literal_eval(headers)
                }
            else:
                request_body = {
                    'url': getattr(parse, 'urljoin')(host, api),
                    'method': method,
                    'json': ast.literal_eval(params),
                    'headers': ast.literal_eval(headers)
                }

            http_client = BaseKeyWords(request_body)
            response = http_client.make_test_templates()
            return self.json(Result(code=1, msg=f'{name} 接口请求成功', data=response))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))
