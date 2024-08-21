from typing import Any, Self

from litestar import Controller, Request, post
from litestar.di import Provide
from litestar.status_codes import HTTP_200_OK

from app.dependencies import provide_user_service
from app.dtos import UserDTO
from app.models import User
from app.schemas import MobileToken, UserLogin
from app.services import UserService


class AccessController(Controller):
    path = "/api/access"
    dependencies = {"user_service": Provide(provide_user_service)}  # noqa: RUF012
    return_dto = UserDTO

    @post("/login")
    async def login(
        self: Self,
        data: UserLogin,
        request: Request[User, Any, Any],
        user_service: UserService,
    ) -> User:
        # TODO: Validate login data.
        user = await user_service.upsert(User(id=data.id))
        request.set_session({"user_id": data.id})
        return user

    @post("/logout", status_code=HTTP_200_OK)
    async def logout(self: Self, request: Request[User, Any, Any]) -> None:
        request.clear_session()
        request.cookies.pop("session")

    @post("/mobile_token")
    async def mobile_token(
        self: Self,
        data: MobileToken,
        request: Request[User, Any, Any],
        user_service: UserService,
    ) -> None:
        request.user.mobile_token = data.token
        await user_service.update(request.user)
