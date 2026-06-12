from datetime import date

from pydantic import BaseModel, Field


class TimelineEventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=220)
    date: date
    type: str = Field(default="生活", max_length=60)
    note: str = ""
    visibility: str = "private"


class CommentCreate(BaseModel):
    author_name: str = Field(min_length=1, max_length=120)
    author_role: str = "visitor"
    body: str = Field(min_length=1, max_length=3000)
