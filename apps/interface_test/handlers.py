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
    InterfacesForm,
    TestCaseForm
)
from apps.interface_test.models import (
    Interfaces,
    TestCases,
    InterfacesTestCase
)
from apps.project.models import Project
from common.core import (
    authenticated_async,
    Response,
    route
)
from common.Recursion import GetJsonParams
from common.httpclient import BaseKeyWords


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
                Response(code=1, msg='接口请求成功', data=response)
            )

        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))


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

        method = self.get_argument('type', None)
        if method is not None:
            interfaces_query = interfaces_query.filter(
                Interfaces.method == method
            )

        url = self.get_argument('router', None)
        if url is not None:
            interfaces_query = interfaces_query.filter(
                Interfaces.url == url
            )

        project = self.get_argument('project', None)
        if project is not None:
            interfaces_query = interfaces_query.filter(
                Project.name == project
            )

        interfaces_query = interfaces_query.order_by(-Project.add_time)
        interfaces = await self.application.objects.execute(interfaces_query)

        for interface in interfaces:
            interface_dict = model_to_dict(interface)
            ret_data.append(interface_dict)

        return self.json(Response(code=1, msg="接口数据查询成功!", data=ret_data))

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
                    Response(code=10020, msg='这个接口已经创建！'))

            except Interfaces.DoesNotExist:
                interface = await self.application.objects.create(
                    Interfaces,
                    interface_name=form.interface_name.data,
                    url=form.url.data,
                    method=form.method.data,
                    headers=form.headers.data,
                    params=form.params.data,
                    project=form.project.data,
                    creator=self.current_user,
                    desc=form.desc.data
                )

                return self.json(
                    Response(code=1, msg="接口创建成功!", data={'interfaceId': interface.id})
                )

        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))


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
                Response(code=1, msg="接口删除成功!", data={"id": interface_id})
            )
        except Interfaces.DoesNotExist:
            self.set_status(400)
            return self.json(Response(code=10020, msg="该接口尚未创建!"))

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
                existed_interface.headers = form.headers.data
                existed_interface.params = form.params.data
                existed_interface.project = form.project.data
                existed_interface.desc = form.desc.data

                await self.application.objects.update(existed_interface)
                return self.json(
                    Response(code=1, msg="接口更新成功!", data={"id": interface_id})
                )

            except Interfaces.DoesNotExist:
                self.set_status(400)
                return self.json(Response(code=10020, msg="接口不存在!"))

        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))


@route(r'/cases/')
class TestCasesHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        用例查询
        """

        ret_data = []
        cases_query = TestCases.extend()

        name = self.get_argument('name', None)

        if name is not None:
            cases_query = cases_query.filter(
                TestCases.test_name == name
            )

        cases_query = cases_query.order_by(-TestCases.add_time)
        cases_query = await self.application.objects.execute(cases_query)

        for case in cases_query:
            case_dict = model_to_dict(case)

            # 用例关联的接口配置
            interfaces_case_query = InterfacesTestCase.extend()
            interfaces_case_query = interfaces_case_query.filter(
                InterfacesTestCase.cases == int(case_dict.get('id'))
            )

            interfaces_case_query = await self.application.objects.execute(interfaces_case_query)
            case_dict.update(
                {
                    'api': [model_to_dict(interfaces_case)for interfaces_case in interfaces_case_query]
                }
            )
            ret_data.append(case_dict)

        return self.json(Response(code=1, msg="用例数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        用例新增
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        form = TestCaseForm.from_json(param)

        if form.validate():

            try:
                await self.application.objects.get(
                    TestCases, test_name=form.test_name.data
                )
                return self.json(
                    Response(code=10020, msg='这个用例已经创建！'))

            except TestCases.DoesNotExist:
                case = await self.application.objects.create(
                    TestCases,
                    test_name=form.test_name.data,
                    assertion=form.assertion.data,
                    db=form.db.data,
                    check_db=form.check_db.data,
                    creator=self.current_user,
                    desc=form.desc.data
                )

                # 接口与用例关联
                if len(form.interfaces.data) > 0:
                    for interface_id in form.interfaces.data:
                        await self.application.objects.create(
                            InterfacesTestCase,
                            cases=case.id,
                            interfaces=interface_id
                        )

                return self.json(
                    Response(
                        code=1, msg="用例创建成功!", data={'caseId': case.id}
                    ))

        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))


@route(r'/cases/([0-9]+)/')
class TestCaseChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, case_id, *args, **kwargs):
        """
        用例删除
        :param case_id: 用例编号
        """
        try:

            # 查询删除用例的接口配置并删除
            cases_query = InterfacesTestCase.extend()

            if case_id is not None:
                cases_query = cases_query.filter(
                    InterfacesTestCase.cases == int(case_id)
                )

            case_interfaces = await self.application.objects.execute(cases_query)

            for case_interface in case_interfaces:
                case_interface_index = model_to_dict(case_interface).get('id')

                interface = await self.application.objects.get(
                    InterfacesTestCase,
                    id=int(case_interface_index)
                )
                await self.application.objects.delete(interface)

            case = await self.application.objects.get(
                TestCases, id=int(case_id)
            )
            await self.application.objects.delete(case)

            return self.json(
                Response(code=1, msg="用例删除成功!", data={"id": case_id})
            )
        except InterfacesTestCase.DoesNotExist:
            self.set_status(400)
            return self.json(Response(code=10020, msg="该用例尚未创建!"))

    @authenticated_async
    async def patch(self, case_id, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestCaseForm.from_json(param)

        if form.validate():

            try:
                existed_case = await self.application.objects.get(TestCases, id=int(case_id))
                existed_case.test_name = form.test_name.data
                existed_case.assertion = form.assertion.data
                existed_case.db = form.db.data
                existed_case.check_db = form.check_db.data
                existed_case.desc = form.desc.data

                await self.application.objects.update(existed_case)

                # 查询修改用例的接口配置并更新最新的接口配置信息
                cases_query = InterfacesTestCase.extend()

                if case_id is not None:
                    cases_query = cases_query.filter(
                        InterfacesTestCase.cases == int(case_id)
                    )

                case_interfaces = await self.application.objects.execute(cases_query)
                case_interface_index = [model_to_dict(case_interface).get('id') for case_interface in case_interfaces]

                if len(form.interfaces.data) > 0:

                    for index, interface_id in enumerate(form.interfaces.data):

                        existed_interfaces = await self.application.objects.get(
                            InterfacesTestCase,
                            id=int(case_interface_index[index])
                        )
                        existed_interfaces.interfaces = interface_id
                        await self.application.objects.update(existed_interfaces)

                return self.json(
                    Response(code=1, msg="用例更新成功!", data={"id": case_id})
                )

            except TestCases.DoesNotExist:
                self.set_status(400)
                return self.json(Response(code=10020, msg="用例不存在!"))

        else:
            self.set_status(400)
            return self.json(Response(code=10090, msg=form.errors))
