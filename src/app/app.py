from typing import TYPE_CHECKING, Any

import pyrogram
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.connection import ASGIConnection
from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)
from litestar.di import Provide
from litestar.middleware.session.server_side import (
    ServerSideSessionBackend,
    ServerSideSessionConfig,
)
from litestar.security.session_auth import SessionAuth
from litestar.stores.redis import RedisStore
from minio import Minio
from redis.asyncio import Redis

from app import controllers
from app.dependencies import provide_user_service
from app.models import User
from app.settings import Settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


async def retrieve_user_handler(
    session: dict[str, Any], connection: ASGIConnection[Any, Any, Any, Any]
) -> User | None:
    db_session = await connection.app.dependencies["db_session"](
        state=connection.app.state, scope=connection.scope
    )
    user_service = await provide_user_service(db_session)
    return await user_service.get_one_or_none(id=session["user_id"])


async def on_startup(app: Litestar) -> None:
    from app.models import Base

    db_engine: AsyncEngine = await app.dependencies["db_engine"](state=app.state)
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    mtproto_client: pyrogram.client.Client = await app.dependencies["mtproto_client"]()
    await mtproto_client.start()


def create_app() -> Litestar:
    settings = Settings()
    auth = SessionAuth[User, ServerSideSessionBackend](
        retrieve_user_handler=retrieve_user_handler,
        session_backend_config=ServerSideSessionConfig(),
        exclude=["/schema", "/api/ping", "/api/access/login"],
    )

    mtproto_client = pyrogram.client.Client(
        "bot", session_string=settings.telegram_session
    )

    minio_client = Minio(
        endpoint=settings.s3_url,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=False,
        cert_check=False,
    )

    return Litestar(
        route_handlers=[
            controllers.ping,
            controllers.PostController,
            controllers.ChannelController,
            controllers.AccessController,
        ],
        on_app_init=[auth.on_app_init],
        on_startup=[on_startup],
        plugins=[
            SQLAlchemyPlugin(
                config=SQLAlchemyAsyncConfig(
                    connection_string=str(settings.database_url),
                    session_config=AsyncSessionConfig(expire_on_commit=False),
                )
            )
        ],
        stores={"sessions": RedisStore(redis=Redis.from_url(str(settings.redis_url)))},
        cors_config=CORSConfig(allow_origins=["*"]),
        dependencies={
            "mtproto_client": Provide(lambda: mtproto_client, sync_to_thread=True),
            "minio_client": Provide(lambda: minio_client, sync_to_thread=True),
        },
    )
