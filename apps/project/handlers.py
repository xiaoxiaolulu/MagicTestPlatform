import json
from abc import ABC
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.project.models import Project
from apps.project.forms import ProjectForm
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

        if name is None:
            return self.json(Result(code=10080, msg="参数有误, 参数name不可缺少"))
        if desc is None:
            return self.json(Result(code=10080, msg="参数有误, 参数desc不可缺少"))

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


class FunctionDebugHandler(BaseHandler, ABC):

    pass


class FunctionHandler(BaseHandler, ABC):

    pass


class FunctionChangeHandler(BaseHandler, ABC):

    pass
