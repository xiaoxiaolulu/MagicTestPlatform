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
import paramiko
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.project.models import Project, TestEnvironment, DBSetting, FunctionGenerator
from apps.project.forms import ProjectForm, TestEnvironmentForm, DBSettingForm, FunctionDebugForm, FunctionGeneratorForm
from apps.utils.Result import Result
from apps.utils.Router import route
from apps.utils.wrappers import authenticated_async


@route(r'/projects/')
class ProjectHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        项目数据查询
        """
        ret_data = []
        project_query = Project.extend()

        # 根据项目名过滤
        name = self.get_argument('name', None)
        if name is not None:
            project_query = project_query.filter(Project.name == name)

        # 默认排序规则
        project_query = project_query.order_by(-Project.add_time)
        projects = await self.application.objects.execute(project_query)
        for project in projects:
            project_dict = model_to_dict(project)
            ret_data.append(project_dict)

        return self.json(Result(code=1, msg="项目数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        新增项目数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = ProjectForm.from_json(param)
        name = form.name.data
        env = form.env.data
        desc = form.desc.data

        if form.validate():
            try:
                existed_project = await self.application.objects.get(Project, name=name)
                return self.json(
                    Result(code=10020, msg='这个项目已经被创建！'))

            except Project.DoesNotExist:
                project = await self.application.objects.create(Project, name=name, desc=desc, creator=self.current_user, env=env)
                return self.json(Result(code=1, msg="创建项目成功!", data={"projectId": project.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


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
            return self.json(Result(code=1, msg="项目删除成功!", data={"id": project_id}))
        except Project.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该项目尚未创建!"))

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
            name = form.name.data
            env = form.env.data
            desc = form.desc.data
            try:
                existed_project = await self.application.objects.get(Project, id=int(project_id))
                existed_project.name = name
                existed_project.env = env
                existed_project.desc = desc
                await self.application.objects.update(existed_project)
                return self.json(Result(code=1, msg="项目更新成功!", data={"id": project_id}))

            except Project.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="项目不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


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
        """
        新增测试环境数据
        """

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
            return self.json(Result(code=1, msg="测试环境删除成功!", data={"id": environment_id}))
        except TestEnvironment.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该环境尚未创建!"))

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


@route('/db_settings/')
class DbSettingHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取数据库配置列表数据
        """
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
        """
        更新数据库配置数据
        """

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
            return self.json(Result(code=1, msg="数据库配置删除成功!", data={"id": db_id}))
        except DBSetting.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该数据库配置尚未创建!"))

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


@route(r'/debug/')
class FunctionDebugHandler(BaseHandler, ABC):

    @staticmethod
    def python_running_env(code):
        """
        python 代码运行环境
        :param code: python代码
        """

        def sftp_exec_command(ssh_client, command):
            try:
                std_in, std_out, std_err = ssh_client.exec_command(command, timeout=4)
                out = "".join([line for line in std_out])
                return out
            except Exception as e:
                print(e)
            return None

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect('172.81.242.70', 22, 'root', 'bubai.4393,')
        sftp_exec_command(ssh_client, "touch test.py")
        sftp_exec_command(ssh_client, f"echo \"{code}\" > test.py")
        response = sftp_exec_command(ssh_client, "python test.py")
        sftp_exec_command(ssh_client, "rm -rf test.py")
        ssh_client.close()
        return response

    def post(self, *args, **kwargs):
        """
        内置函数-自定义python解释器, 并提供代码运行环境用于debug
        """
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = FunctionDebugForm.from_json(param)

        if form.validate():
            code = form.function.data
            result = self.python_running_env(code)

            return self.json(Result(code=1, msg='success', data={'RunningRes': result}))
        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


@route(r'/functions/')
class FunctionHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        """
        获取内置函数列表
        """
        ret_data = []
        function_query = FunctionGenerator.extend()

        # 根据方法名过滤
        name = self.get_argument('name', None)
        if name is not None:
            function_query = function_query.filter(FunctionGenerator.name == name)

        # 默认排序规则
        function_query = function_query.order_by(FunctionGenerator.add_time.desc())

        functions = await self.application.objects.execute(function_query)
        for func in functions:
            func_dict = model_to_dict(func)
            ret_data.append(func_dict)

        return self.json(Result(code=1, msg="函数方法数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        """
        增加内置函数数据
        """

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = FunctionGeneratorForm.from_json(param)
        name = form.name.data
        function = form.function.data
        desc = form.desc.data

        if form.validate():
            try:
                existed_function = await self.application.objects.get(FunctionGenerator, name=name)
                return self.json(
                    Result(code=10020, msg='这个函数方法已经被创建！'))

            except FunctionGenerator.DoesNotExist:
                function = await self.application.objects.create(FunctionGenerator, name=name, desc=desc,
                                                                 function=function, creator=self.current_user)
                return self.json(Result(code=1, msg="创建函数方法成功!", data={"functionId": function.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


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
            return self.json(Result(code=1, msg="函数方法删除成功!", data={"functionId": function_id}))
        except FunctionGenerator.DoesNotExist:
            self.set_status(400)
            return self.json(Result(code=10020, msg="该函数方法尚未创建!"))

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
            name = form.name.data
            function = form.function.data
            desc = form.desc.data

            try:
                existed_function = await self.application.objects.get(FunctionGenerator, id=int(function_id))
                existed_function.name = name
                existed_function.function = function
                existed_function.desc = desc
                await self.application.objects.update(existed_function)
                return self.json(Result(code=1, msg="函数方法更新成功!", data={"id": function_id}))

            except FunctionGenerator.DoesNotExist:
                self.set_status(404)
                return self.json(Result(code=10020, msg="该函数方法不存在!"))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))
