from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, Self

import pyrogram
from litestar import Controller, Request, get, post, put
from litestar.di import Provide
from litestar.params import Parameter
from sqlalchemy import select

from app import dtos
from app.dependencies import provide_post_service
from app.models import Post, User
from app.schemas import PostCreate, PostUpdate
from app.services import PostService

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class PostController(Controller):
    path = "/api/posts"
    dependencies = {"post_service": Provide(provide_post_service)}  # noqa: RUF012
    return_dto = dtos.PostDTO

    @post()
    async def create_post(
        self: Self,
        data: PostCreate,
        post_service: PostService,
        mtproto_client: pyrogram.client.Client,
    ) -> Post:
        message = await mtproto_client.send_message(
            chat_id="agV2bstmSSew6LRb9ZTcKkyl7Mfx8cBS", text=data.text
        )
        post = await post_service.upsert({**data.model_dump(), "preview": message.link})
        # if data.photos is None:
        #     return post
        # for photo in data.photos:
        #     minio_client.make_bucket(f"post{post.id}")
        #     fp = BytesIO()
        #     fp.write(base64.b64decode(photo.content))
        #     minio_client.put_object(
        #         bucket_name=f"post{post.id}",
        #         object_name=photo.name,
        #         data=fp,
        #         length=fp.getbuffer().nbytes,
        #     )
        return post

    @put()
    async def update_post(
        self: Self,
        data: PostUpdate,
        post_service: PostService,
        mtproto_client: pyrogram.client.Client,
    ) -> Post:
        message = await mtproto_client.send_message(
            chat_id="agV2bstmSSew6LRb9ZTcKkyl7Mfx8cBS", text=data.text
        )
        return await post_service.upsert({**data.model_dump(), "preview": message.link})

    @get("/draft")
    async def list_drafts(
        self: Self,
        request: Request[User, Any, Any],
        post_service: PostService,
        channel_id: Annotated[int | None, Parameter(query="channelId")] = None,
    ) -> list[Post]:
        stmt = (
            select(Post)
            .where(Post.scheduled_at.is_(None))
            .where(Post.channel_id.in_(channel.id for channel in request.user.channels))
        )
        if isinstance(channel_id, int):
            stmt = stmt.where(Post.channel_id == channel_id)
        result = await post_service.repository.session.scalars(stmt)
        return list(result.all())

    @get("/scheduled")
    async def list_scheduled(
        self: Self,
        request: Request[User, Any, Any],
        post_service: PostService,
        channel_id: Annotated[int | None, Parameter(query="channelId")] = None,
    ) -> list[Post]:
        stmt = (
            select(Post)
            .where(Post.scheduled_at > datetime.now(UTC))
            .where(Post.channel_id.in_(channel.id for channel in request.user.channels))
        )
        if isinstance(channel_id, int):
            stmt = stmt.where(Post.channel_id == channel_id)
        result = await post_service.repository.session.scalars(stmt)
        return list(result.all())

    @get("/sent")
    async def list_sent(
        self: Self,
        request: Request[User, Any, Any],
        post_service: PostService,
        channel_id: Annotated[int | None, Parameter(query="channelId")] = None,
    ) -> list[Post]:
        stmt = (
            select(Post)
            .where(Post.scheduled_at <= datetime.now(UTC))
            .where(Post.channel_id.in_(channel.id for channel in request.user.channels))
        )
        if isinstance(channel_id, int):
            stmt = stmt.where(Post.channel_id == channel_id)
        result = await post_service.repository.session.scalars(stmt)
        return list(result.all())

    @get("/{post_id:int}")
    async def get_post(self: Self, post_id: int, post_service: PostService) -> Post:
        return await post_service.get(post_id)
