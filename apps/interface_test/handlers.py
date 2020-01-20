"""
    接口测试模块
    ———————
            |
            |---接口管理
            |
            |---公共参数
            |
            |---测试用例
            |
            |---测试套件
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
    TestCaseForm,
    PublicParamsForm,
    TestSuiteForm
)
from apps.interface_test.models import (
    Interfaces,
    TestCases,
    InterfacesTestCase,
    CheckDbContent,
    PublicParams,
    TestSuite,
    TestCaseSuite
)
from apps.project.models import Project
from common.validator import JsonResponse
from common.core import (
    authenticated_async,
    route
)
from common.Recursion import GetJsonParams
from common.httpclient import BaseKeyWords


@route(r'/public_params/')
class PublicParamsHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取公共参数列表
        """

        ret_data = []
        public_params_query = PublicParams.extend()

        name = self.get_argument('name', None)
        if name is not None:
            public_params_query = public_params_query.filter(
                PublicParams.name == name
            )

        public_params_query = public_params_query.order_by(-PublicParams.add_time)
        public_params = await self.application.objects.execute(public_params_query)

        for public_param in public_params:
            public_param_dict = model_to_dict(public_param)
            ret_data.append(public_param_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        新增公共参数
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = PublicParamsForm.from_json(param)

        if form.validate():

            try:
                await self.application.objects.get(
                    PublicParams,
                    name=form.name.data
                )
                return self.json(
                    JsonResponse(code=10007))

            except PublicParams.DoesNotExist:
                public_params = await self.application.objects.create(
                    PublicParams,
                    name=form.name.data,
                    params_type=form.params_type.data,
                    params=form.params.data,
                    creator=self.current_user
                )

                return self.json(
                    JsonResponse(code=1, data={'paramsId': public_params.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/public_params/([0-9]+)/')
class PublicParamsChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, param_id, *args, **kwargs):
        """
        删除公共参数
        :param param_id: 参数id
        """
        try:
            public_params = await self.application.objects.get(PublicParams, id=int(param_id))
            await self.application.objects.delete(public_params)
            return self.json(
                JsonResponse(code=1, data={"id": param_id})
            )
        except PublicParams.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009))

    @authenticated_async
    async def patch(self, param_id, *args, **kwargs):
        """
        修改公共参数
        :param param_id: 参数id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = PublicParamsForm.from_json(param)

        if form.validate():

            try:
                existed_public_param = await self.application.objects.get(PublicParams, id=int(param_id))
                existed_public_param.name = form.name.data
                existed_public_param.params_type = form.params_type.data
                existed_public_param.params = form.params.data
                await self.application.objects.update(existed_public_param)
                return self.json(
                    JsonResponse(code=1, data={"id": param_id})
                )

            except PublicParams.DoesNotExist:
                self.set_status(404)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


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
                JsonResponse(code=1, data=response)
            )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


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

        interfaces_query = interfaces_query.order_by(-Interfaces.add_time)
        interfaces = await self.application.objects.execute(interfaces_query)

        for interface in interfaces:
            interface_dict = model_to_dict(interface)
            ret_data.append(interface_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

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
                    JsonResponse(code=10007))

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
                    JsonResponse(code=1, data={'interfaceId': interface.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/interfaces/([0-9]+)/')
class InterfacesChangeHandler(BaseHandler, ABC):

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
                JsonResponse(code=1, data={"id": interface_id})
            )
        except Interfaces.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009))

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
                    JsonResponse(code=1, data={"id": interface_id})
                )

            except Interfaces.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


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

            # 用例关联落库校验数据
            db_check_query = CheckDbContent.extend()
            db_check_query = db_check_query.filter(
                CheckDbContent.case == int(case_dict.get('id'))
            )

            db_check_query = await self.application.objects.execute(db_check_query)

            db_checks = []

            for db_check in db_check_query:
                db_check_dict = model_to_dict(db_check)
                db = db_check_dict.get('db').get('id')
                assert_sql = db_check_dict.get('check_db')
                db_checks.append(
                    {'db': db, 'assertSql': assert_sql}
                )

            case_dict.update({'db_check': db_checks})
            ret_data.append(case_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        用例新增
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestCaseForm.from_json(param)

        if form.validate():

            try:
                await self.application.objects.get(
                    TestCases, test_name=form.test_name.data
                )
                return self.json(
                    JsonResponse(code=10007))

            except TestCases.DoesNotExist:
                case = await self.application.objects.create(
                    TestCases,
                    test_name=form.test_name.data,
                    assertion=param.get('assertion'),
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

                # 落库校验与用例关联
                db_check_content = param.get('db_check')
                for db_content in db_check_content:
                    db = db_content.get('db')
                    content = db_content.get('assertSql')
                    await self.application.objects.create(
                        CheckDbContent,
                        db=db,
                        check_db=content,
                        case=case.id
                    )

                return self.json(
                    JsonResponse(
                        code=1, data={'caseId': case.id}
                    ))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


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

            # 删除用例关联的落库数据
            db_check_query = CheckDbContent.extend()
            if case_id is not None:
                db_check_query = db_check_query.filter(
                    CheckDbContent.case == int(case_id)
                )

            db_checks = await self.application.objects.execute(db_check_query)

            for db_check in db_checks:
                db_check_index = model_to_dict(db_check).get('id')

                db_assert = await self.application.objects.get(
                    CheckDbContent,
                    id=int(db_check_index)
                )
                await self.application.objects.delete(db_assert)

            case = await self.application.objects.get(
                TestCases, id=int(case_id)
            )
            await self.application.objects.delete(case)

            return self.json(
                JsonResponse(code=1, data={"id": case_id})
            )
        except InterfacesTestCase.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009))

    @authenticated_async
    async def patch(self, case_id, *args, **kwargs):
        """
        用例修改
        :param case_id: 用例id
        """

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
                    JsonResponse(code=1, data={"id": case_id})
                )

            except TestCases.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/cases_run/([0-9]+)/')
class TestCaseRunHandler(BaseHandler, ABC):

    @authenticated_async
    async def post(self, case_id, *args, **kwargs):
        """

        :param case_id:
        :param args:
        :param kwargs:
        :return:
        """

        cases_content = []
        cases_query = TestCases.extend()

        cases_query = cases_query.where(TestCases.id == case_id).order_by(-TestCases.add_time)
        cases_query = await self.application.objects.execute(cases_query)

        for case in cases_query:
            case_dict = model_to_dict(case)

            # 用例关联的接口配置
            interfaces_case_query = InterfacesTestCase.extend()
            interfaces_case_query = interfaces_case_query.filter(
                InterfacesTestCase.cases == int(case_dict.get('id'))
            )

            interfaces_case_query = await self.application.objects.execute(interfaces_case_query)

            # 获取用例名称
            name = GetJsonParams.get_value(case_dict, 'test_name')

            # 获取断言配置
            assertion = GetJsonParams.get_value(case_dict, 'assertion')

            # 获取Api配置信息
            body = []
            interfaces = [model_to_dict(interfaces_case) for interfaces_case in interfaces_case_query]
            for interface in interfaces:

                interface_query = Interfaces.extend().where(Interfaces.id == interface.get('interfaces').get('id'))
                interface_query = await self.application.objects.execute(interface_query)
                for _index, _interface in enumerate(interface_query):
                    _interface = model_to_dict(_interface)

                    # 获取host配置信息
                    project_query = Project.extend().filter(Project.id == _interface.get('project').get('id'))
                    projects = await self.application.objects.execute(project_query)
                    host = GetJsonParams.get_value(model_to_dict(projects[_index]), 'host_address')
                    temp = ('url', 'params', 'headers')
                    request_body = GetJsonParams.for_keys_to_dict(host, *temp, my_dict=_interface)
                    body.append({_interface.get('interface_name'): request_body})

            # 用例关联落库校验数据
            db_check_query = CheckDbContent.extend()
            db_check_query = db_check_query.filter(
                CheckDbContent.case == int(case_dict.get('id'))
            )

            db_check_query = await self.application.objects.execute(db_check_query)

            db_checks = []

            for db_check in db_check_query:
                db_check_dict = model_to_dict(db_check)
                db = db_check_dict.get('db').get('id')
                assert_sql = db_check_dict.get('check_db')
                db_checks.append(
                    {'db': db, 'assertSql': assert_sql}
                )

            cases_content.append({'name': name, "body": body, 'assert': assertion, 'dbCheck': db_checks})

        # TODO: 上下文管理器类, 生成器函数,自动创建Unittest用例, 批量运行测试用例

        return self.json(JsonResponse(code=1, data=cases_content))


@route(r'/suites/')
class TestSuiteHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取测试套件列表
        """

        ret_data = []
        suites_query = TestSuite.extend()

        name = self.get_argument('name', None)

        if name is not None:
            suites_query = suites_query.filter(
                TestSuite.suite_name == name
            )

        suites_query = suites_query.order_by(-TestSuite.add_time)
        suites_query = await self.application.objects.execute(suites_query)

        for suite in suites_query:
            suite_dict = model_to_dict(suite)

            # 测试套件关联的测试用例
            suite_case_query = TestCaseSuite.extend()
            suite_case_query = suite_case_query.filter(
                TestCaseSuite.suite == int(suite_dict.get('id'))
            )

            suite_case_query = await self.application.objects.execute(suite_case_query)
            suite_dict.update(
                {
                    'case': [model_to_dict(suite_case)for suite_case in suite_case_query]
                }
            )

            ret_data.append(suite_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        新增测试套件
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestSuiteForm.from_json(param)

        if form.validate():

            try:
                await self.application.objects.get(
                    TestSuite, suite_name=form.suite_name.data
                )
                return self.json(
                    JsonResponse(code=10007))

            except TestSuite.DoesNotExist:
                suite = await self.application.objects.create(
                    TestSuite,
                    suite_name=form.suite_name.data,
                    creator=self.current_user,
                    desc=form.desc.data
                )

                # 套件与用例关联
                if len(form.cases.data) > 0:
                    for case_id in form.cases.data:
                        await self.application.objects.create(
                            TestCaseSuite,
                            suite=suite.id,
                            cases=case_id
                        )

                return self.json(
                    JsonResponse(
                        code=1, data={'suiteId': suite.id}
                    ))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/suites/([0-9]+)/')
class TestSuiteChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, suite_id, *args, **kwargs):
        """
        删除测试套件
        :param suite_id: 测试套件id
        """

        try:

            # 查询删除用例的接口配置并删除
            suites_query = TestCaseSuite.extend()

            if suite_id is not None:
                suites_query = suites_query.filter(
                    TestCaseSuite.suite == int(suite_id)
                )

            suite_cases = await self.application.objects.execute(suites_query)

            for suite_case in suite_cases:
                suite_case_index = model_to_dict(suite_case).get('id')

                cases = await self.application.objects.get(
                    TestCaseSuite,
                    id=int(suite_case_index)
                )
                await self.application.objects.delete(cases)

            suite = await self.application.objects.get(
                TestSuite, id=int(suite_id)
            )
            await self.application.objects.delete(suite)

            return self.json(
                JsonResponse(code=1, data={"id": suite_id})
            )
        except TestCaseSuite.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009))

    @authenticated_async
    async def patch(self, suite_id, *args, **kwargs):
        """
        修改测试套件
        :param suite_id: 套件id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestSuiteForm.from_json(param)

        if form.validate():

            try:
                existed_suite = await self.application.objects.get(TestSuite, id=int(suite_id))
                existed_suite.suite_name = form.suite_name.data
                existed_suite.desc = form.desc.data

                await self.application.objects.update(existed_suite)

                # 修改套件关联的测试用例
                suites_query = TestCaseSuite.extend()

                if suite_id is not None:
                    suites_query = suites_query.filter(
                        TestCaseSuite.suite == int(suite_id)
                    )

                case_suites = await self.application.objects.execute(suites_query)
                case_suite_index = [model_to_dict(case_suite).get('id') for case_suite in case_suites]

                if len(form.cases.data) > 0:
                    # 对于修改时未删减原有配置并新增一条用例配置时, 则对testCaseSuite中间表进行新增操作, 防止程序抛出IndexError.

                    for index, case_id in enumerate(form.cases.data):

                        try:
                            existed_cases = await self.application.objects.get(
                                TestCaseSuite,
                                id=int(case_suite_index[index])
                            )
                            existed_cases.cases = case_id
                            await self.application.objects.update(existed_cases)
                        except IndexError:
                            await self.application.objects.create(
                                TestCaseSuite,
                                suite=suite_id,
                                cases=case_id
                            )

                return self.json(
                    JsonResponse(code=1, data={"id": suite_id})
                )

            except TestSuite.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


class TestSuiteRunHandler(BaseHandler, ABC):

    @authenticated_async
    async def post(self, suite_id, *args, **kwargs):
        """
        API1 -----|--- Case1 ---|------|
        API2 -----|                    |
        API3 -----|                    |---- Suites1
                                       |
        API4 -----|--- Case2 ---|------|
        API5 -----|
        API6 -----|
        """

        # TODO: 同测试用例运行接口, 开发老大太吵了，心情都没了， Last day等下班
        pass
