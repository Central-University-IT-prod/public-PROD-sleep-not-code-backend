from typing import Annotated

from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Channel, Post, User

UserDTO = SQLAlchemyDTO[
    Annotated[
        User,
        SQLAlchemyDTOConfig(
            exclude={
                "channels",
                "mobile_token",
            },
            rename_strategy="camel",
        ),
    ]
]


PostDTO = SQLAlchemyDTO[
    Annotated[
        Post,
        SQLAlchemyDTOConfig(
            exclude={
                "tg_id",
                "channel",
                "files",
            },
            rename_strategy="camel",
        ),
    ]
]

ChannelDTO = SQLAlchemyDTO[
    Annotated[
        Channel,
        SQLAlchemyDTOConfig(
            exclude={
                "users",
                "posts",
            },
            rename_strategy="camel",
        ),
    ]
]
