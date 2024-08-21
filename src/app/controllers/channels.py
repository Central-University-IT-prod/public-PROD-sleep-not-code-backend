import contextlib
from typing import Any, Self

import pyrogram
from litestar import Controller, Request, get, post
from litestar.di import Provide
from litestar.exceptions import PermissionDeniedException
from sqlalchemy import select

from app.dependencies import provide_channel_service
from app.dtos import ChannelDTO
from app.models import Channel, User
from app.schemas import ChannelCreate
from app.services import ChannelService


class ChannelController(Controller):
    path = "/api/channels"
    return_dto = ChannelDTO
    dependencies = {  # noqa: RUF012
        "channel_service": Provide(provide_channel_service),
    }

    @post()
    async def create_channel(
        self: Self,
        data: ChannelCreate,
        mtproto_client: pyrogram.client.Client,
        channel_service: ChannelService,
        request: Request[User, Any, Any],
    ) -> Channel:
        with contextlib.suppress(
            pyrogram.errors.exceptions.bad_request_400.UserAlreadyParticipant
        ):
            await mtproto_client.join_chat(data.url)

        chat = await mtproto_client.get_chat(data.url)

        try:
            members: list[pyrogram.types.ChatMember] = [
                member
                async for member in mtproto_client.get_chat_members(  # type: ignore[union-attr]
                    chat.id, filter=pyrogram.enums.ChatMembersFilter.ADMINISTRATORS
                )
            ]
        except pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired as e:
            raise PermissionDeniedException from e

        flag = False
        for member in members:
            if member.user.id == request.user.id:
                flag = True
                break

        if flag is False:
            raise PermissionDeniedException

        channel = await channel_service.upsert(Channel(id=chat.id, name=chat.title))
        await channel_service.add_user(request.user, channel)
        return channel

    @get("/{channel_id:int}")
    async def get_channel(
        self: Self, channel_id: int, channel_service: ChannelService
    ) -> Channel:
        return await channel_service.get(channel_id)

    @get()
    async def list_channels(
        self: Self, request: Request[User, Any, Any], channel_service: ChannelService
    ) -> list[Channel]:
        result = await channel_service.repository.session.scalars(
            select(Channel).where(Channel.users.any(id=request.user.id))
        )
        return list(result.all())
