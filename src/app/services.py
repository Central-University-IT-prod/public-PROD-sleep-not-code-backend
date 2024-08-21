from typing import Self

from advanced_alchemy import SQLAlchemyAsyncRepositoryService

from app.models import Channel, Post, User
from app.repositories import ChannelRepository, PostRepository, UserRepository


class UserService(SQLAlchemyAsyncRepositoryService[User]):
    repository_type = UserRepository


class ChannelService(SQLAlchemyAsyncRepositoryService[Channel]):
    repository_type = ChannelRepository

    async def add_user(self: Self, user: User, channel: Channel) -> None:
        channel.users.append(user)
        await self.repository.session.commit()


class PostService(SQLAlchemyAsyncRepositoryService[Post]):
    repository_type = PostRepository
