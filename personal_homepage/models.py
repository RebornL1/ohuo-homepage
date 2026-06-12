from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .db import Base


def json_list_column():
    return mapped_column(MutableList.as_mutable(JSON().with_variant(JSONB(), "postgresql")), default=list)


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    title: Mapped[str] = mapped_column(String(220))
    summary: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text, default="")
    visibility: Mapped[str] = mapped_column(String(20), index=True, default="public")
    comment_policy: Mapped[str] = mapped_column(String(30), default="visitor")
    tags: Mapped[list[str]] = json_list_column()
    published_at: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ToolItem(Base):
    __tablename__ = "tool_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True)
    status: Mapped[str] = mapped_column(String(60), default="自用中")
    description: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(500), default="")
    tags: Mapped[list[str]] = json_list_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220))
    body: Mapped[str] = mapped_column(Text)
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    written_at: Mapped[date] = mapped_column(Date, default=date.today)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220))
    event_type: Mapped[str] = mapped_column(String(60), default="生活")
    note: Mapped[str] = mapped_column(Text, default="")
    happened_at: Mapped[date] = mapped_column(Date, index=True, default=date.today)
    visibility: Mapped[str] = mapped_column(String(20), default="private")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FilmWork(Base):
    __tablename__ = "film_works"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(220), unique=True)
    year: Mapped[str] = mapped_column(String(20), default="")
    role: Mapped[str] = mapped_column(String(160), default="")
    summary: Mapped[str] = mapped_column(Text)
    cover_url: Mapped[str] = mapped_column(String(500), default="")
    references: Mapped[list[str]] = json_list_column()
    visibility: Mapped[str] = mapped_column(String(20), default="public")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_slug: Mapped[str] = mapped_column(String(140), index=True)
    author_name: Mapped[str] = mapped_column(String(120))
    author_role: Mapped[str] = mapped_column(String(40), default="visitor")
    body: Mapped[str] = mapped_column(Text)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(260), unique=True)
    original_name: Mapped[str] = mapped_column(String(260))
    storage_path: Mapped[str] = mapped_column(String(700))
    public_url: Mapped[str] = mapped_column(String(700))
    mime_type: Mapped[str] = mapped_column(String(160), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
