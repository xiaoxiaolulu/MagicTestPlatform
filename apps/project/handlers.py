"""
    项目管理模块
    ———————
            |
            |---内置函数
            |
            |---项目配置
            |
            |---数据库配置
            |
            |---环境配置
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import json
from abc import ABC
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.project.models import (
    Project,
    TestEnvironment,
    DBSetting,
    FunctionGenerator
)
from apps.project.forms import (
    ProjectForm,
    TestEnvironmentForm,
    DBSettingForm,
    FunctionDebugForm,
    FunctionGeneratorForm
)
from common.validator import JsonResponse
from common.core import (
    authenticated_async,
    route,
    python_running_env
)


@route(r'/projects/')
class ProjectHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        项目数据查询
        """
        ret_data = []
        project_query = Project.extend()

        name = self.get_argument('name', None)
        if name is not None:
            project_query = project_query.filter(Project.name == name)

        env = self.get_argument('env', None)
        if env is not None:
            project_query = project_query.filter(TestEnvironment.name == env)

        host = self.get_argument('host', None)
        if host is not None:
            project_query = project_query.filter(TestEnvironment.host_address == host)

        project_query = project_query.order_by(-Project.add_time)
        projects = await self.application.objects.execute(project_query)
        for project in projects:
            project_dict = model_to_dict(project)
            ret_data.append(project_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        新增项目数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = ProjectForm.from_json(param)
        name = form.name.data

        if form.validate():
            try:
                await self.application.objects.get(Project, name=name)
                return self.json(
                    JsonResponse(code=10007))

            except Project.DoesNotExist:
                project = await self.application.objects.create(
                    Project,
                    name=name,
                    desc=form.desc.data,
                    env=form.env.data,
                    creator=self.current_user
                )
                return self.json(
                    JsonResponse(code=1, data={"projectId": project.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/projects/([0-9]+)/')
class ProjectChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, project_id, *args, **kwargs):
        """
        删除项目数据
        :param project_id: 删除的项目id
        """
        try:
            project = await self.application.objects.get(Project, id=int(project_id))
            await self.application.objects.delete(project)
            return self.json(
                JsonResponse(code=1, data={"id": project_id})
            )
        except Project.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10007))

    @authenticated_async
    async def patch(self, project_id, *args, **kwargs):
        """
        更新项目数据
        :param project_id: 更新的项目id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = ProjectForm.from_json(param)

        if form.validate():

            try:
                existed_project = await self.application.objects.get(Project, id=int(project_id))
                existed_project.name = form.name.data
                existed_project.env = form.env.data
                existed_project.desc = form.desc.data
                await self.application.objects.update(existed_project)
                return self.json(
                    JsonResponse(code=1, data={"id": project_id})
                )

            except Project.DoesNotExist:
                self.set_status(404)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/test_envs/')
class TestEnvironmentHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取测试环境列表数据
        """
        ret_data = []
        environment_query = TestEnvironment.extend()

        # 根据环境名过滤
        name = self.get_argument('name', None)
        if name is not None:
            environment_query = environment_query.filter(
                TestEnvironment.name == name
            )

        host = self.get_argument('router', None)
        if host is not None:
            environment_query = environment_query.filter(
                TestEnvironment.host_address == host
            )

        # 默认排序规则
        environment_query = environment_query.order_by(
            TestEnvironment.add_time.desc()
        )

        environments = await self.application.objects.execute(environment_query)
        for environment in environments:
            environment_dict = model_to_dict(environment)
            ret_data.append(environment_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        新增测试环境数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestEnvironmentForm.from_json(param)
        name = form.name.data

        if form.validate():
            try:
                await self.application.objects.get(TestEnvironment, name=name)
                return self.json(
                    JsonResponse(code=10007, msg='这个测试环境已经被创建！'))

            except TestEnvironment.DoesNotExist:
                environment = await self.application.objects.create(
                    TestEnvironment,
                    name=name,
                    host_address=form.host_address.data,
                    desc=form.desc.data,
                    creator=self.current_user
                )
                return self.json(
                    JsonResponse(
                        code=1, data={"EnvironmentId": environment.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/test_envs/([0-9]+)/')
class TestEnvironmentChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, environment_id, *args, **kwargs):
        """
        删除测试环境数据
        :param environment_id: 删除环境的id
        """
        try:
            environment = await self.application.objects.get(TestEnvironment, id=int(environment_id))
            await self.application.objects.delete(environment)
            return self.json(
                JsonResponse(code=1, data={"id": environment_id})
            )
        except TestEnvironment.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009, msg="该环境尚未创建!"))

    @authenticated_async
    async def patch(self, environment_id, *args, **kwargs):
        """
        更新测试环境数据
        :param environment_id: 更新的测试环境id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestEnvironmentForm.from_json(param)

        if form.validate():

            try:
                existed_environment = await self.application.objects.get(TestEnvironment, id=int(environment_id))
                existed_environment.name = form.name.data
                existed_environment.host = form.host_address.data
                existed_environment.desc = form.desc.data
                await self.application.objects.update(existed_environment)
                return self.json(
                    JsonResponse(code=1, data={"id": environment_id})
                )

            except TestEnvironment.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009, msg="该环境不存在!"))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route('/db_settings/')
class DbSettingHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取数据库配置列表数据
        """
        ret_data = []
        db_query = DBSetting.extend()

        name = self.get_argument('name', None)

        if name is not None:
            db_query = db_query.filter(DBSetting.name == name)

        db_type = self.get_argument('type', None)
        if db_type is not None:
            db_query = db_query.filter(DBSetting.db_type == db_type)

        # 默认排序规则
        db_query = db_query.order_by(DBSetting.add_time.desc())

        dbs = await self.application.objects.execute(db_query)
        for db in dbs:
            db_dict = model_to_dict(db)
            ret_data.append(db_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        更新数据库配置数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = DBSettingForm.from_json(param)
        name = form.name.data

        if form.validate():
            try:
                await self.application.objects.get(DBSetting, name=name)
                return self.json(JsonResponse(code=10007))

            except DBSetting.DoesNotExist:
                db = await self.application.objects.create(
                    DBSetting,
                    name=name,
                    db_type=form.db_type.data,
                    db_password=form.db_password.data,
                    db_user=form.db_user.data,
                    db_host=form.db_host.data,
                    db_port=form.db_port.data,
                    desc=form.desc.data,
                    creator=self.current_user
                )
                return self.json(
                    JsonResponse(
                        code=1, data={"DBId": db.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/db_settings/([0-9]+)/')
class DbSettingChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, db_id, *args, **kwargs):
        """
        删除数据库配置
        :param db_id: 删除的配置数据库id
        """
        try:
            db = await self.application.objects.get(DBSetting, id=int(db_id))
            await self.application.objects.delete(db)
            return self.json(
                JsonResponse(
                    code=1, data={"id": db_id})
            )
        except DBSetting.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009, msg="该数据库配置尚未创建!"))

    @authenticated_async
    async def patch(self, db_id, *args, **kwargs):
        """
        更新数据配置
        :param db_id: 更新的配置数据库id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = DBSettingForm.from_json(param)

        if form.validate():

            try:
                existed_db = await self.application.objects.get(DBSetting, id=int(db_id))
                existed_db.name = form.name.data
                existed_db.db_user = form.db_user.data
                existed_db.db_type = form.db_type.data
                existed_db.db_host = form.db_host.data
                existed_db.db_password = form.db_password.data
                existed_db.db_port = form.db_port.data
                existed_db.desc = form.desc.data
                await self.application.objects.update(existed_db)
                return self.json(
                    JsonResponse(code=1, data={"id": db_id})
                )

            except DBSetting.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/debug/')
class FunctionDebugHandler(BaseHandler, ABC):

    def post(self, *args, **kwargs):
        """
        内置函数-自定义python解释器, 并提供代码运行环境用于debug
        """
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = FunctionDebugForm.from_json(param)

        if form.validate():
            code = form.function.data
            result = python_running_env(code)

            return self.json(
                JsonResponse(code=1, data={'RunningRes': result})
            )
        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/functions/')
class FunctionHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取内置函数列表
        """
        ret_data = []
        function_query = FunctionGenerator.extend()

        name = self.get_argument('name', None)
        if name is not None:
            function_query = function_query.filter(
                FunctionGenerator.name == name
            )

        function_query = function_query.order_by(
            FunctionGenerator.add_time.desc()
        )

        functions = await self.application.objects.execute(function_query)
        for func in functions:
            func_dict = model_to_dict(func)
            ret_data.append(func_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        增加内置函数数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = FunctionGeneratorForm.from_json(param)
        name = form.name.data

        if form.validate():
            try:
                await self.application.objects.get(FunctionGenerator, name=name)
                return self.json(
                    JsonResponse(code=10007)
                )

            except FunctionGenerator.DoesNotExist:
                function = await self.application.objects.create(
                    FunctionGenerator,
                    name=name,
                    desc=form.desc.data,
                    function=form.function.data,
                    creator=self.current_user
                )
                return self.json(
                    JsonResponse(code=1, data={"functionId": function.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/functions/([0-9]+)/')
class FunctionChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, function_id, *args, **kwargs):
        """
        删除内置函数数据
        :param function_id: 删除内置函数数据id
        """
        try:
            function = await self.application.objects.get(FunctionGenerator, id=int(function_id))
            await self.application.objects.delete(function)
            return self.json(
                JsonResponse(code=1, data={"functionId": function_id})
            )
        except FunctionGenerator.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009, msg="该函数方法尚未创建!"))

    @authenticated_async
    async def patch(self, function_id, *args, **kwargs):
        """
        更新内置函数数据
        :param function_id: 更新内置函数数据的id
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = FunctionGeneratorForm.from_json(param)

        if form.validate():

            try:
                existed_function = await self.application.objects.get(FunctionGenerator, id=int(function_id))
                existed_function.name = form.name.data
                existed_function.function = form.function.data
                existed_function.desc = form.desc.data
                await self.application.objects.update(existed_function)
                return self.json(
                    JsonResponse(
                        code=1, data={"id": function_id})
                )

            except FunctionGenerator.DoesNotExist:
                self.set_status(400)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004))
