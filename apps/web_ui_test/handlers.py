"""
    web Ui测试模块
    ———————
            |
            |---元素管理
            |
            |---测试用例
            |
            |---测试套件
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import json
from abc import ABC
from SeleniumLibrary import *
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.web_ui_test.forms import PageElementForm
from apps.web_ui_test.models import PageElement
from common.validator import JsonResponse
from common.core import (
    authenticated_async,
    route
)


@route(r'/get_keywords/')
class RobotFrameWorkKeyWordsHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        keyword = [
            keyword.title().translate(str.maketrans('_', ' '))
            for keyword in SeleniumLibrary().get_keyword_names()
        ]
        return self.json(JsonResponse(code=1, data={'keyword': keyword}))


@route(r'/page_element/')
class PageElementHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):

        ret_data = []
        page_element_query = PageElement.extend()

        name = self.get_argument('name', None)
        if name is not None:
            page_element_query = page_element_query.filter(
                page_element_query.element_name == name
            )

        page = self.get_argument('page', None)
        if page is not None:
            page_element_query = page_element_query.filter(
                page_element_query.owner_page == page
            )

        page_element_query = page_element_query.order_by(-PageElement.add_time)
        page_elements = await self.application.objects.execute(page_element_query)

        for page_element in page_elements:
            page_element_dict = model_to_dict(page_element)
            ret_data.append(page_element_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = PageElementForm.from_json(param)

        if form.validate():

            try:
                await self.application.objects.get(
                    PageElement,
                    element_name=form.element_name.data
                )
                return self.json(
                    JsonResponse(code=10007))

            except PageElement.DoesNotExist:
                page_element = await self.application.objects.create(
                    PageElement,
                    element_name=form.element_name.data,
                    operate_type=form.operate_type.data,
                    owner_page=form.owner_page.data,
                    creator=self.current_user,
                    desc=form.desc.data
                )

                return self.json(
                    JsonResponse(code=1, data={'Id': page_element.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))


@route(r'/page_element/([0-9]+)/')
class PageElementChangeHandler(BaseHandler, ABC):

    @authenticated_async
    async def delete(self, element_id, *args, **kwargs):
        try:
            element = await self.application.objects.get(PageElement, id=int(element_id))
            await self.application.objects.delete(element)
            return self.json(
                JsonResponse(code=1, data={"id": element_id})
            )
        except PageElement.DoesNotExist:
            self.set_status(400)
            return self.json(JsonResponse(code=10009))

    @authenticated_async
    async def patch(self, element_id, *args, **kwargs):

        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        form = PageElementForm.from_json(param)

        if form.validate():

            try:
                existed_element = await self.application.objects.get(PageElement, id=int(element_id))
                existed_element.element_name = form.element_name.data
                existed_element.operate_type = form.operate_type.data
                existed_element.owner_page = form.owner_page.data
                existed_element.desc = form.desc.data
                await self.application.objects.update(existed_element)
                return self.json(
                    JsonResponse(code=1, data={"id": element_id})
                )

            except PageElement.DoesNotExist:
                self.set_status(404)
                return self.json(JsonResponse(code=10009))

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))
