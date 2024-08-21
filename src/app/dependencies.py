from sqlalchemy.ext.asyncio import AsyncSession

from app.services import ChannelService, PostService, UserService


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(session=db_session, auto_commit=True)


async def provide_post_service(db_session: AsyncSession) -> PostService:
    return PostService(session=db_session, auto_commit=True)


async def provide_channel_service(db_session: AsyncSession) -> ChannelService:
    return ChannelService(session=db_session, auto_commit=True)
