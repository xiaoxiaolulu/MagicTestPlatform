import functools
import jwt
from apps.users.models import User
from apps.utils.parse_settings import settings


def authenticated_async(method):
    @functools.wraps(method)
    async def wrapper(self, *args, **kwargs):
        authorization = self.request.headers.get('Authorization', None)
        if authorization:
            try:
                jwt_data = jwt.decode(
                    authorization,
                    settings.TORNADO_CONF.secret_key,
                    leeway=settings.TORNADO_CONF.jwt_expire,
                    options={"verify_exp": True}
                )

                user_id = jwt_data["id"]
                # 从数据库中获取到user并设置给_current_user
                try:
                    user = await self.application.objects.get(User, id=user_id)
                    self._current_user = user
                    await method(self, *args, **kwargs)
                except User.DoesNotExist:
                    self.set_status(401)
            except jwt.ExpiredSignatureError:
                self.set_status(401)
        else:
            self.set_status(401)
            self.finish({})
    return wrapper

