import json
from abc import ABC
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.project.models import Project, TestEnvironment, DBSetting
from apps.project.forms import ProjectForm, TestEnvironmentForm, DBSettingForm
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
                existed_environment = await self.application.objects.get(TestEnvironment, name=name)
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


class DbSettingHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        ret_data = []
        db_query = DBSetting.extend()

        # 根据环境名过滤
        name = self.get_argument('name', None)
        if name is not None:
            db_query = db_query.filter(DBSetting.name == name)

        # 默认排序规则
        db_query = db_query.order_by(DBSetting.add_time.desc())

        dbs = await self.application.objects.execute(db_query)
        for db in dbs:
            db_dict = model_to_dict(db)
            ret_data.append(db_dict)

        return self.json(Result(code=1, msg="数据库配置数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = DBSettingForm.from_json(param)
        name = form.name.data
        user = form.db_user.data
        db_type = form.db_type.data
        host = form.db_host.data
        password = form.db_password.data
        port = form.db_port.data
        desc = form.desc.data

        if form.validate():
            try:
                existed_db = await self.application.objects.get(DBSetting, name=name)
                return self.json(
                    Result(code=10020, msg='这个数据库已经被创建！'))

            except DBSetting.DoesNotExist:
                db = await self.application.objects.create(
                    DBSetting, name=name, db_type=db_type, db_password=password, db_user=user,
                    db_host=host, db_port=port, desc=desc, creator=self.current_user)
                return self.json(Result(code=1, msg="创建数据库成功!", data={"DBId": db.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class DbSettingChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, db_id, *args, **kwargs):
        try:
            db = await self.application.objects.get(DBSetting, id=int(db_id))
            await self.application.objects.delete(db)
            return self.json(Result(code=1, msg="数据库配置删除成功!", data={"id": db_id}))
        except DBSetting.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该数据库配置尚未创建!"))

    @authenticated_async
    async def patch(self, db_id, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = DBSettingForm.from_json(param)

        if form.validate():
            name = form.name.data
            db_type = form.db_type.data
            host = form.db_host.data
            user = form.db_user.data
            password = form.db_password.data
            port = form.db_port.data
            desc = form.desc.data

            try:
                existed_db = await self.application.objects.get(DBSetting, id=int(db_id))
                existed_db.name = name
                existed_db.db_user = user
                existed_db.db_type = db_type
                existed_db.db_host = host
                existed_db.db_password = password
                existed_db.db_port = port
                existed_db.desc = desc
                await self.application.objects.update(existed_db)
                return self.json(Result(code=1, msg="数据库配置更新成功!", data={"id": db_id}))

            except DBSetting.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="该数据库配置不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class FunctionDebugHandler(BaseHandler, ABC):

    pass


class FunctionHandler(BaseHandler, ABC):

    pass


class FunctionChangeHandler(BaseHandler, ABC):

    pass
