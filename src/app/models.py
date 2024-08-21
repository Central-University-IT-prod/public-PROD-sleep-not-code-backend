from datetime import UTC, datetime

from advanced_alchemy.base import CommonTableAttributes, orm_registry
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import BigInteger, Column, ForeignKey, Table, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(CommonTableAttributes, DeclarativeBase):
    registry = orm_registry


user_to_channel = Table(
    "user_to_channel",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("channel_id", ForeignKey("channel.id"), primary_key=True),
)


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, unique=True)
    mobile_token: Mapped[str | None] = mapped_column(Text(), unique=True, default=None)

    channels: Mapped[list["Channel"]] = relationship(
        secondary=user_to_channel, back_populates="users", lazy="selectin"
    )


class Channel(Base):
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, unique=True)
    name: Mapped[str]

    users: Mapped[list[User]] = relationship(
        secondary=user_to_channel, back_populates="channels", lazy="selectin"
    )
    posts: Mapped[list["Post"]] = relationship(
        lazy="selectin", back_populates="channel"
    )


class Post(Base):
    id: Mapped[int] = mapped_column(
        BigInteger(), primary_key=True, unique=True, autoincrement=True
    )
    tg_id: Mapped[int | None] = mapped_column(BigInteger(), unique=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channel.id"))
    name: Mapped[str]
    text: Mapped[str] = mapped_column(Text())
    comment: Mapped[str | None] = mapped_column(Text())
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTimeUTC(), default=None)
    updated_at: Mapped[datetime] = mapped_column(
        DateTimeUTC(), default=datetime.now(UTC)
    )
    preview: Mapped[str | None]

    channel: Mapped["Channel"] = relationship(lazy="selectin", back_populates="posts")
