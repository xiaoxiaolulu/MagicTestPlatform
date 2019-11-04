import json
from abc import ABC
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.project.models import Project, TestEnvironment
from apps.project.forms import ProjectForm, TestEnvironmentForm
from apps.utils.Result import Result
from apps.utils.async_decorators import authenticated_async


class ProjectHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        ret_data = []
        project_query = Project.extend()

        # 根据项目名过滤
        name = self.get_argument('name', None)
        if name is not None:
            project_query = project_query.filter(Project.name == name)

        # 默认排序规则
        project_query = project_query.order_by(Project.add_time.desc())

        projects = await self.application.objects.execute(project_query)
        for project in projects:
            project_dict = model_to_dict(project)
            ret_data.append(project_dict)

        return self.json(Result(code=1, msg="项目数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = ProjectForm.from_json(param)
        name = form.name.data
        desc = form.desc.data

        if form.validate():
            try:
                existed_project = await self.application.objects.get(Project, name=name)
                return self.json(
                    Result(code=10020, msg='这个项目已经被创建！'))

            except Project.DoesNotExist:
                project = await self.application.objects.create(Project, name=name, desc=desc, creator=self.current_user)
                return self.json(Result(code=1, msg="创建项目成功!", data={"projectId": project.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class ProjectChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, project_id, *args, **kwargs):
        try:
            project = await self.application.objects.get(Project, id=int(project_id))
            await self.application.objects.delete(project)
            return self.json(Result(code=1, msg="项目删除成功!", data={"id": project_id}))
        except Project.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该项目尚未创建!"))

    @authenticated_async
    async def patch(self, project_id, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = ProjectForm.from_json(param)

        if form.validate():
            name = form.name.data
            desc = form.desc.data
            try:
                existed_project = await self.application.objects.get(Project, id=int(project_id))
                existed_project.name = name
                existed_project.desc = desc
                await self.application.objects.update(existed_project)
                return self.json(Result(code=1, msg="项目更新成功!", data={"id": project_id}))

            except Project.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="项目不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class TestEnvironmentHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        ret_data = []
        environment_query = TestEnvironment.extend()

        # 根据环境名过滤
        name = self.get_argument('name', None)
        if name is not None:
            environment_query = environment_query.filter(TestEnvironment.name == name)

        # 默认排序规则
        environment_query = environment_query.order_by(TestEnvironment.add_time.desc())

        environments = await self.application.objects.execute(environment_query)
        for environment in environments:
            environment_dict = model_to_dict(environment)
            ret_data.append(environment_dict)

        return self.json(Result(code=1, msg="测试环境数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestEnvironmentForm.from_json(param)
        name = form.name.data
        host = form.host_address.data
        desc = form.desc.data

        if form.validate():
            try:
                existed_environment = await self.application.objects.get(Project, name=name)
                return self.json(
                    Result(code=10020, msg='这个测试环境已经被创建！'))

            except TestEnvironment.DoesNotExist:
                environment = await self.application.objects.create(TestEnvironment, name=name, host_address=host, desc=desc, creator=self.current_user)
                return self.json(Result(code=1, msg="创建测试环境成功!", data={"EnvironmentId": environment.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class TestEnvironmentChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, environment_id, *args, **kwargs):
        try:
            environment = await self.application.objects.get(TestEnvironment, id=int(environment_id))
            await self.application.objects.delete(environment)
            return self.json(Result(code=1, msg="测试环境删除成功!", data={"id": environment_id}))
        except TestEnvironment.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该环境尚未创建!"))

    @authenticated_async
    async def patch(self, environment_id, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = TestEnvironmentForm.from_json(param)

        if form.validate():
            name = form.name.data
            host = form.host_address.data
            desc = form.desc.data

            try:
                existed_environment = await self.application.objects.get(TestEnvironment, id=int(environment_id))
                existed_environment.name = name
                existed_environment.host = host
                existed_environment.desc = desc
                await self.application.objects.update(existed_environment)
                return self.json(Result(code=1, msg="环境更新成功!", data={"id": environment_id}))

            except TestEnvironment.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="该环境不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class FunctionDebugHandler(BaseHandler, ABC):

    pass


class FunctionHandler(BaseHandler, ABC):

    pass


class FunctionChangeHandler(BaseHandler, ABC):

    pass
