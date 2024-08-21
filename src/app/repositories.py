from advanced_alchemy import SQLAlchemyAsyncRepository

from app.models import Channel, Post, User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    model_type = User


class PostRepository(SQLAlchemyAsyncRepository[Post]):
    model_type = Post


class ChannelRepository(SQLAlchemyAsyncRepository[Channel]):
    model_type = Channel
