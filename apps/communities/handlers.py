import json
import os
import uuid
from abc import ABC
import aiofiles
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler, RedisHandler
from apps.communities.forms import CommunityGroupForm, GroupApplyForm, PostForm, CommentForm
from apps.communities.models import CommunityGroup, CommunityGroupMember, Post, PostComment
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


class GroupDetailHandler(BaseHandler, RedisHandler, ABC):

    @authenticated_async
    async def get(self, group_id, *args, **kwargs):
        try:
            group = await self.application.objects.get(CommunityGroup, id=int(group_id))
            item_dict = dict()
            item_dict['name'] = group.name
            item_dict['id'] = group.id
            item_dict['desc'] = group.desc
            item_dict['notice'] = group.notice
            item_dict['member_nums'] = group.member_nums
            item_dict['post_nums'] = group.post_nums
            item_dict['cover'] = '{}/media/{}'.format(self.settings['SITE_URL'], group.cover)
            self.json(Result(code=1, msg="success", data=item_dict))
        except CommunityGroup.DoesNotExist:
            self.set_status(404)


class PostHandler(BaseHandler, RedisHandler, ABC):

    @authenticated_async
    async def get(self, group_id, *args, **kwargs):
        ret_data = []
        try:
            group = await self.application.objects.get(CommunityGroup, id=int(group_id))
            group_member = await self.application.objects.get(CommunityGroupMember, group=group, user=self.current_user,
                                                              status='agree')

            post_query = Post.extend()

            # 排序
            order = self.get_argument('order', None)
            if order:
                if order == '-add_time':
                    post_query = post_query.order_by(Post.add_time.desc())

            posts = await self.application.objects.execute(post_query)
            for post in posts:
                item_dict = {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'comment_nums': post.comment_nums,
                    'user': {
                        'id': post.user.id,
                        'nick_name': post.user.nick_name
                    }
                }
                ret_data.append(item_dict)

            return self.json(Result(code=1, msg="success", data=ret_data))

        except CommunityGroup.DoesNotExist:
            self.set_status(404)
        except CommunityGroupMember.DoesNotExist:
            self.set_status(403)

    @authenticated_async
    async def post(self, group_id, *args, **kwargs):
        params = self.request.body.decode('utf-8')
        params = json.loads(params)
        form = PostForm.from_json(params)

        if form.validate():

            try:
                group = await self.application.objects.get(CommunityGroup, id=int(group_id))
                group_member = await self.application.objects.get(CommunityGroupMember, group=group, user=self.current_user, status='agree')

                post = await self.application.objects.create(Post,
                                                             group=group, user=self.current_user,
                                                             title=form.title.data,
                                                             content=form.content.data)
                return self.json(Result(code=1, msg="success", data={"id": post.id}))
            except CommunityGroup.DoesNotExist:
                self.set_status(404)
            except CommunityGroupMember.DoesNotExist:
                self.set_status(403)
        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))


class PostDetailHandler(BaseHandler, RedisHandler, ABC):

    @authenticated_async
    async def get(self, post_id, *args, **kwargs):
        ret_data = {}
        try:
            posts_query = Post.extend().where(Post.id == int(post_id))
            posts = await self.application.objects.execute(posts_query)
            for data in posts:
                item_dict = dict()
                item_dict['user'] = model_to_dict(data.user)
                ret_data.update(item_dict)
            return self.json(Result(code=1, msg="success", data=ret_data))
        except Post.DoesNotExist:
            self.set_status(404)


class PostCommentHandler(BaseHandler, RedisHandler, ABC):

    @authenticated_async
    async def get(self, post_id, *args, **kwargs):
        ret_data = []
        try:
            post = await self.application.objects.get(Post, id=int(post_id))
            comment_query = PostComment.extend().where(PostComment.post == post, PostComment.parent_comment.is_null(True)).order_by(
                PostComment.add_time.desc()
            )
            post_comments = await self.application.objects.execute(comment_query)
            for item in post_comments:
                item_dict = {
                    'user': model_to_dict(item.user),
                    'content': item.content,
                    'reply_nums': item.reply_nums,
                    'like_nums': item.like_nums,
                    'id': item.id
                }
                ret_data.append(item_dict)
                return self.json(Result(code=1, msg='success', data=ret_data))
        except Post.DoestNotExist:
            self.set_status(404)

    @authenticated_async
    async def post(self, post_id, *args, **kwargs):
        params = self.request.body.decode('utf-8')
        params = json.loads(params)
        form = CommentForm.from_json(params)

        if form.validate():
            try:
                post = await self.application.objects.get(Post, id=int(post_id))
                comment = await self.application.objects.create(PostComment, user=self.current_user, post=post,
                                                                content=form.content.data)
                post.comment_nums += 1
                await self.application.object.update(post)
                return self.json(Result(code=1, msg="success", data={"id": comment.id, "user": self.current_user.nick_name}))
            except Post.DoesNotExist:
                self.set_status(404)
        else:
            self.set_status(400)
            return self.json(Result(code=10090, msg=form.errors))
