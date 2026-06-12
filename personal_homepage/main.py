from contextlib import asynccontextmanager
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine, get_db
from .models import Comment, ContentItem, FilmWork, JournalEntry, MediaAsset, TimelineEvent, ToolItem
from .schemas import CommentCreate, TimelineEventCreate
from .seed import seed_database
from .settings import settings

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
MEDIA_ROOT = settings.media_root
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.auto_seed:
        with SessionLocal() as db:
            seed_database(db)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/assets", StaticFiles(directory=ROOT_DIR / "assets"), name="assets")
app.mount(settings.public_media_url, StaticFiles(directory=MEDIA_ROOT), name="media")


def row_to_dict(row, date_fields: tuple[str, ...] = ()) -> dict:
    payload = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    for field in date_fields:
        if payload.get(field):
            payload[field] = payload[field].isoformat()
    return payload


def homepage_payload(db: Session) -> dict:
    content_items = db.scalars(select(ContentItem).order_by(ContentItem.published_at.desc())).all()
    tools = db.scalars(select(ToolItem).order_by(ToolItem.created_at.desc())).all()
    journals = db.scalars(select(JournalEntry).order_by(JournalEntry.written_at.desc())).all()
    timeline = db.scalars(select(TimelineEvent).order_by(TimelineEvent.happened_at.desc())).all()
    works = db.scalars(select(FilmWork).order_by(FilmWork.year.desc())).all()

    return {
        "app_name": settings.app_name,
        "principles": [
            {
                "label": "01",
                "title": "知识要能复用",
                "body": "每篇学习总结都尽量沉淀成可链接、可引用、可更新的 wiki 节点。",
            },
            {
                "label": "02",
                "title": "工具要能持续用",
                "body": "记录自己真正长期使用的小工具，而不是一次性的 demo。",
            },
            {
                "label": "03",
                "title": "生活要能回看",
                "body": "用时间线连接关键事件、日记、作品和思考，保留成长路径。",
            },
        ],
        "articles": [row_to_dict(item, ("published_at", "created_at")) for item in content_items],
        "tools": [row_to_dict(item, ("created_at",)) for item in tools],
        "journals": [row_to_dict(item, ("written_at", "created_at")) for item in journals],
        "timeline": [row_to_dict(item, ("happened_at", "created_at")) for item in timeline],
        "works": [row_to_dict(item, ("created_at",)) for item in works],
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"request": request, "data": homepage_payload(db)},
    )


@app.get("/api/content")
def list_content(db: Session = Depends(get_db)):
    return homepage_payload(db)["articles"]


@app.get("/api/timeline")
def list_timeline(db: Session = Depends(get_db)):
    return homepage_payload(db)["timeline"]


@app.post("/api/timeline", status_code=201)
def create_timeline_event(payload: TimelineEventCreate, db: Session = Depends(get_db)):
    event = TimelineEvent(
        title=payload.title,
        event_type=payload.type,
        note=payload.note,
        happened_at=payload.date,
        visibility=payload.visibility,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return row_to_dict(event, ("happened_at", "created_at"))


@app.post("/api/content/{slug}/comments", status_code=201)
def create_comment(slug: str, payload: CommentCreate, db: Session = Depends(get_db)):
    item = db.scalar(select(ContentItem).where(ContentItem.slug == slug))
    if not item:
        raise HTTPException(status_code=404, detail="Content item not found")
    if item.comment_policy == "closed":
        raise HTTPException(status_code=403, detail="Comments are closed")
    if item.comment_policy == "member" and payload.author_role != "member":
        raise HTTPException(status_code=403, detail="Member role required")

    comment = Comment(
        content_slug=slug,
        author_name=payload.author_name,
        author_role=payload.author_role,
        body=payload.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return row_to_dict(comment, ("created_at",))


@app.post("/api/media", status_code=201)
def upload_media(file: UploadFile = File(...), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".pdf"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid4().hex}{suffix}"
    target = MEDIA_ROOT / filename
    with target.open("wb") as handle:
        copyfileobj(file.file, handle)

    public_url = f"{settings.public_media_url.rstrip('/')}/{filename}"
    asset = MediaAsset(
        filename=filename,
        original_name=file.filename or filename,
        storage_path=str(target),
        public_url=public_url,
        mime_type=file.content_type or "",
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return row_to_dict(asset, ("created_at",))
