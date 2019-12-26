"""
    测试工具模块
    ———————
            |
            |---关键字检索
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
from os import path
from abc import ABC
import aiofiles
import shortuuid
from playhouse.shortcuts import model_to_dict
from MagicTestPlatform.handlers import BaseHandler
from apps.test_tools.forms import ImageIdentifyTextForm
from apps.test_tools.models import ImageIdentifyText
from common.core import (
    authenticated_async,
    route,
    format_arguments,
    image_identifying_text,
    async_image_identifying_text
)
from common.parse_settings import settings
from common.validator import JsonResponse


@route(r'/images_search/')
class ProjectHandler(BaseHandler, ABC):

    @authenticated_async
    async def get(self, *args, **kwargs):
        ret_data = []
        images_query = ImageIdentifyText.extend()

        name = self.get_argument('name', None)
        if name is not None:
            images_query = images_query.filter(
                ImageIdentifyText.image_name == name
            )

        images_query = images_query.order_by(-ImageIdentifyText.add_time)
        images = await self.application.objects.execute(images_query)

        for image in images:
            image_dict = model_to_dict(image)
            image_dict['address'] = "{}/media/{}/".format(
                settings.TORNADO_CONF.SITE_URL, image.address
            )

            # 根据图片中的关键字进行检索
            keywords = self.get_argument('keywords', None)
            if keywords is not None:

                if image.content.__contains__(keywords):
                    ret_data.append(image_dict)
            else:
                ret_data.append(image_dict)

        return self.json(JsonResponse(code=1, data=ret_data))

    @authenticated_async
    async def post(self, *args, **kwargs):

        body = self.request.body_arguments
        body = format_arguments(body)
        form = ImageIdentifyTextForm(body)

        if form.validate():
            files_meta = self.request.files.get("image")

            try:
                await self.application.objects.get(ImageIdentifyText, image_name=form.image_name.data)
                return self.json(
                    JsonResponse(code=10007))

            except ImageIdentifyText.DoesNotExist:

                new_filename, content = None, None
                if files_meta:
                    # 完成图片保存并将值设置给对应的记录
                    # 通过aiofiles写文件
                    for meta in files_meta:
                        filename = meta["filename"]
                        new_filename = "{uuid}_{filename}".format(
                            uuid=shortuuid.uuid(), filename=filename
                        )
                        filepath = path.join(
                            settings.TORNADO_CONF.MEDIA_ROOT, new_filename
                        )
                        async with aiofiles.open(filepath, 'wb') as f:
                            await f.write(meta['body'])

                        # 识别图片文字, 识别速度1~3秒左右
                        words_result = dict(await async_image_identifying_text(filepath)).get('words_result')
                        content = ','.join([word_result.get('words') for word_result in words_result])

                image = await self.application.objects.create(
                    ImageIdentifyText,
                    image_name=form.image_name.data,
                    desc=form.desc.data,
                    address=new_filename,
                    creator=self.current_user,
                    content=content
                )

                return self.json(
                    JsonResponse(code=1, data={"Id": image.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))