import asyncio
import datetime

import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.models import Channel, Post, User


class FCMManager:
    def __init__(self, cred: credentials.Certificate) -> None:
        self.cred = cred

    def initialize(self) -> None:
        firebase_admin.initialize_app(self.cred)

    async def send_notifications(self, session: AsyncSession) -> None:
        thirty_minutes_from_now = (datetime.datetime.now(datetime.UTC) +
                                   datetime.timedelta(minutes=30))
        results = await session.scalars(
            select(Post)
            .join(Channel)
            .join(Channel.users)
            .where(Post.scheduled_at >= thirty_minutes_from_now)
            .where(Post.scheduled_at <= thirty_minutes_from_now +
                   datetime.timedelta(minutes=1))
            .where(User.mobile_token.is_not(None))
        )
        posts = results.all()
        if posts:
            for post in posts:
                print(post.id)
                for user in post.channel.users:
                    print(user.mobile_token)
                    message = messaging.Message(
                        data={
                            "title": "Предупреждение!",
                            "text": f'Менее чем через 30 минут будет опубликован пост "{post.name}"',
                        },
                        token=user.mobile_token,
                    )
                    resp = messaging.send(message)
                    print(resp)


cred = credentials.Certificate("postpulsefcm-firebase-adminsdk-brd0d-260dc04e5e.json") # тут что-то не так с путем. либо указывать относительный, либо еще что-то
manager = FCMManager(cred)
manager.initialize()
database_url = "postgresql+asyncpg://secret@localhost:5432/postgres"
engine = create_async_engine(database_url)


async def run_continuously() -> None:
    while True:
        async with AsyncSession(engine) as session:
            await manager.send_notifications(session)
        await asyncio.sleep(60)


async def main() -> None:
    await run_continuously()


if __name__ == "__main__":
    asyncio.run(main())

