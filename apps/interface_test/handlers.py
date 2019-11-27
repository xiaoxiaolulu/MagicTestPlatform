import ast
import json
from abc import ABC
from urllib import parse
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.interface_test.forms import InterfacesDebugForm, InterfacesForm
from apps.interface_test.models import Interfaces
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


@route(r'/interfaces/')
class InterfacesHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        接口列表查询
        """

        ret_data = []
        interfaces_query = Interfaces.extend()

        name = self.get_argument('name', None)
        if name is not None:
            interfaces_query = interfaces_query.filter(Interfaces.interface_name == name)

        interfaces_query = interfaces_query.order_by(-Project.add_time)
        interfaces = await self.application.objects.execute(interfaces_query)

        for interface in interfaces:
            interface_dict = model_to_dict(interface)
            ret_data.append(interface_dict)

        return self.json(Result(code=1, msg="接口数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        创建接口
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = InterfacesForm.from_json(param)

        if form.validate():

            name = form.interface_name.data
            api = form.url.data
            method = form.method.data
            headers = form.method.data
            params = form.params.data
            assertion = form.assertion.data
            db = form.db.data
            check_db = form.check_db.data
            response_extraction = form.response_extraction.data
            project = form.project.data
            desc = form.desc.data

            try:
                existed_interface = await self.application.objects.get(Interfaces, interface_name=name)
                return self.json(
                    Result(code=10020, msg='这个接口已经创建！'))

            except Interfaces.DoesNotExist:
                interface = await self.application.objects.create(
                    Interfaces,
                    interface_name=name,
                    url=api,
                    method=method,
                    headers=headers,
                    params=params,
                    assertion=assertion,
                    db=db,
                    check_db=check_db,
                    response_extraction=response_extraction,
                    project=project,
                    desc=desc,
                    creator=self.current_user)

                return self.json(Result(code=1, msg="接口创建成功!", data={'interfaceId': interface.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))
