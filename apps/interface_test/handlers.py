"""
    接口测试模块
    ———————
            |
            |---接口管理
            |
            |---测试用例管理
            |
            |---测试套件管理
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import ast
import json
from abc import ABC
from urllib import parse
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.interface_test.forms import (
    InterfacesDebugForm,
    InterfacesForm
)
from apps.interface_test.models import Interfaces
from apps.project.models import Project
from apps.utils import (
    authenticated_async,
    Result,
    route
)
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
            return self.json(
                Result(code=1, msg=f'{name} 接口请求成功', data=response)
            )

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
            interfaces_query = interfaces_query.filter(
                Interfaces.interface_name == name
            )

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

            try:
                await self.application.objects.get(
                    Interfaces, interface_name=form.interface_name.data
                )
                return self.json(
                    Result(code=10020, msg='这个接口已经创建！'))

            except Interfaces.DoesNotExist:
                interface = await self.application.objects.create(
                    Interfaces,
                    interface_name=form.interface_name.data,
                    url=form.url.data,
                    method=form.method.data,
                    headers=form.method.data,
                    params=form.params.data,
                    assertion=form.assertion.data,
                    db=form.db.data,
                    check_db=form.check_db.data,
                    response_extraction=form.response_extraction.data,
                    project=form.project.data,
                    desc=form.desc.data,
                    creator=self.current_user
                )

                return self.json(
                    Result(code=1, msg="接口创建成功!", data={'interfaceId': interface.id})
                )

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


@route(r'/interfaces/([0-9]+)/')
class ProjectChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, interface_id, *args, **kwargs):
        """
        删除接口数据
        :param interface_id: 删除的接口id
        """
        try:
            interface = await self.application.objects.get(Interfaces, id=int(interface_id))
            await self.application.objects.delete(interface)
            return self.json(
                Result(code=1, msg="接口删除成功!", data={"id": interface_id})
            )
        except Interfaces.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该接口尚未创建!"))

    @authenticated_async
    async def patch(self, interface_id, *args, **kwargs):
        """
        更新接口数据
        :param interface_id: 更新的接口id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = InterfacesForm.from_json(param)

        if form.validate():

            try:
                existed_interface = await self.application.objects.get(Interfaces, id=int(interface_id))
                existed_interface.interface_name = form.interface_name.data
                existed_interface.url = form.url.data
                existed_interface.method = form.method.data
                existed_interface.headers = form.method.data
                existed_interface.params = form.params.data
                existed_interface.assertion = form.assertion.data
                existed_interface.db = form.db.data
                existed_interface.check_db = form.check_db.data
                existed_interface.response_extraction = form.response_extraction.data
                existed_interface.project = form.project.data
                existed_interface.desc = form.desc.data

                await self.application.objects.update(existed_interface)
                return self.json(
                    Result(code=1, msg="接口更新成功!", data={"id": interface_id})
                )

            except Interfaces.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="接口不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))