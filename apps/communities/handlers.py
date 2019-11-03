import json
import os
import uuid
from abc import ABC
import aiofiles
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.communities.forms import CommunityGroupForm, GroupApplyForm
from apps.communities.models import CommunityGroup, CommunityGroupMember
from apps.utils.Result import Result
from apps.utils.async_decorators import authenticated_async


class GroupHandler(BaseHandler, RedisHandler, ABC):

    async def get(self, *args, **kwargs):
        ret_data = []
        group_query = CommunityGroup.extend()

        # 根据类别进行过滤
        ctg = self.get_argument('ctg', None)
        if ctg:
            group_query = group_query.filter(CommunityGroup.category == ctg)

        # 根据参数进行排序
        order = self.get_argument('order', None)
        if order:
            if order == 'post_nums':
                group_query = group_query.order_by(CommunityGroup.post_nums.desc())
            if order == 'member_nums':
                group_query = group_query.order_by(CommunityGroup.member_nums.desc())
            if order == 'add_time':
                group_query = group_query.order_by(CommunityGroup.add_time.desc())

        groups = await self.application.objects.execute(group_query)
        for group in groups:
            group_dict = model_to_dict(group)
            group_dict['cover'] = "{}/media/{}".format(self.settings["SITE_URL"], group_dict['cover'])
            ret_data.append(group_dict)

        return self.json(Result(code=1, msg="小组数据查询成功!", data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):
        form = CommunityGroupForm(self.request.body_arguments)
        if form.validate():
            files_meta = self.request.files.get('cover', None)
            if not files_meta:
                self.set_status(400)
                return self.json(Result(code=10090, msg="请上传头像!"))
            else:
                # 文件保存在设置的对应位置
                new_filename = ""
                for meta in files_meta:
                    filename = meta['filename']
                    new_filename = '{uuid}_{filename}'.format(uuid=uuid.uuid1(), filename=filename)
                    file_path = os.path.join(self.settings['MEDIA_ROOT'], new_filename)
                    async with aiofiles.open(file_path, mode='wb') as stream:
                        await stream.write(meta['body'])

                group = await self.application.objects.create(CommunityGroup, creator=self.current_user,
                                                              name=form.name.data, category=form.category.data,
                                                              desc=form.desc.data, notice=form.notice.data,
                                                              cover=new_filename)

                return self.json(Result(code=1, msg="创建小组成功!", data={'id': group.id}))

        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class GroupMemberHandler(BaseHandler, RedisHandler, ABC):

    @authenticated_async
    async def post(self, group_id, *args, **kwargs):
        params = self.request.body.decode('utf-8')
        params = json.loads(params)
        form = GroupApplyForm.from_json(params)
        if form.validate():
            try:
                group = await self.application.objects.get(CommunityGroup, id=int(group_id))
                existed = await self.application.objects.get(CommunityGroupMember, group=group, user=self.current_user)
                self.set_status(400)
                return self.json(Result(code=10080, msg="用户已经加入该小组"))
            except CommunityGroup.DoesNotExist:
                self.set_status(404)
            except CommunityGroupMember.DoesNotExit:
                group_members = await self.application.objects.create(
                    CommunityGroupMember, group=group, user=self.current_user,
                    apply_reason=form.apply_reason.data
                )
                return self.json(Result(code=1, msg="创建小组成功", data={"id": group_members.id}))
        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))
