from datetime import datetime

import pydantic
from pydantic.alias_generators import to_camel


class Photo(pydantic.BaseModel):
    name: str
    content: str


class PostCreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=to_camel)

    channel_id: int
    name: str
    text: str
    comment: str | None = None
    scheduled_at: datetime | None = None
    photos: list[Photo] | None = None


class PostUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=to_camel)

    id: int
    channel_id: int
    name: str
    text: str
    comment: str | None = None
    scheduled_at: datetime | None = None
    photos: list[Photo] | None = None


class ChannelCreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=to_camel)

    url: str


class UserLogin(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=to_camel)

    id: int
    first_name: str
    last_name: str
    username: str
    photo_url: str
    auth_date: datetime
    hash: str


class MobileToken(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(alias_generator=to_camel)

    token: str
