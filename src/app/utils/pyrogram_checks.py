import asyncio
import datetime

import aiocron
from pyrogram import Client, enums
from pyrogram.types import InputMediaPhoto
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models import Post

app = Client(
    "my_account",
    api_id=21738396,
    api_hash="XXX",
)
channel_link_for_preview = "e774e1d2af57045ecbe0b7b6c96ae7b9"


async def get_channel_id(username: str) -> int | None:
    channel = None
    try:
        channel = await app.get_chat(username)
    except Exception:
        if username.startswith("https"):
            channel = await app.get_chat(username.replace("https://t.me/", ""))
        elif username.startswith("t.me"):
            channel = await app.get_chat(username.replace("t.me/", ""))
    if channel:
        return channel.id
    return None


async def get_channel_admins_ids(channel_id: int):  # noqa: ANN201
    administrators = []
    async for m in app.get_chat_members(
        channel_id, filter=enums.ChatMembersFilter.ADMINISTRATORS
    ):
        administrators.append(m.user.id)  # noqa: PERF401

    return administrators


async def join_bot_to_channel(channel_link: str) -> None:
    await app.join_chat(channel_link)


async def send_post(channel_id: int, files: list[str], caption: str) -> None:
    if files:
        media = []
        for i, file in enumerate(files):
            if i == 0:
                media.append(InputMediaPhoto(media=file, caption=caption))
            else:
                media.append(InputMediaPhoto(media=file))

        await app.send_media_group(chat_id=channel_id, media=media)
    else:
        await app.send_message(chat_id=channel_id, text=caption)


async def main() -> None:
    database_url = "postgresql+asyncpg://secret@localhost:5432/postgres"
    engine = create_async_engine(database_url)
    channel_username = "e774e1d2af57045ecbe0b7b6c96ae7b9"

    @aiocron.crontab("*/1 * * * *")
    async def send_post_cron() -> None:
        async with app:
            channel_id = await get_channel_id(channel_username)
            session = AsyncSession(engine)
            async with session:
                result = await session.scalars(
                    select(Post)
                    .where(Post.scheduled_at >= datetime.datetime.now(datetime.UTC))
                    .where(
                        Post.scheduled_at
                        <= datetime.datetime.now(datetime.UTC)
                        + datetime.timedelta(minutes=1)
                    )
                    .order_by(Post.scheduled_at)
                )

                posts = result.all()
                for post in posts:
                    print(f"{post.id}\n\n\n{post.scheduled_at}")
                    await send_post(channel_id, [], post.text)


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
