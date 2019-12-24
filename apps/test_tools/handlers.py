"""
    测试工具模块
    ———————
            |
            |---关键字检索
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DESCRIPTION

    :copyright: (c) 2019 by Null.
"""
import json
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
    format_arguments
)
from common.parse_settings import settings
from common.validator import JsonResponse


@route(r'/images_search/')
class ProjectHandler(BaseHandler, ABC):

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

                new_filename = None
                if files_meta:
                    # 完成图片保存并将值设置给对应的记录
                    # 通过aiofiles写文件
                    for meta in files_meta:
                        filename = meta["filename"]
                        new_filename = "{uuid}_{filename}".format(
                            uuid=shortuuid.uuid(), filename=filename
                        )
                        file_path = path.join(
                            settings.TORNADO_CONF.MEDIA_ROOT, new_filename
                        )
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(meta['body'])

                image = await self.application.objects.create(
                    ImageIdentifyText,
                    image_name=form.image_name.data,
                    desc=form.desc.data,
                    address=new_filename,
                    creator=self.current_user
                )

                return self.json(
                    JsonResponse(code=1, data={"Id": image.id})
                )

        else:
            self.set_status(400)
            return self.json(JsonResponse(code=10004, msg=form.errors))