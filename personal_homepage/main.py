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
        "self_distillation": [
            {
                "title": "抽象概念与心理学",
                "signal": "概念学习 / 心理学打卡",
                "metric": "12",
                "unit": "连续打卡",
                "summary": "记录抽象概念、心理学主题、认知模型和阶段性理解变化。",
                "items": ["自我叙事", "依恋模式", "动机系统", "认知偏差"],
                "source": "手动记录 / 课程笔记 / wiki",
            },
            {
                "title": "游戏人格切片",
                "signal": "Steam / 小黑盒",
                "metric": "128h",
                "unit": "累计游玩",
                "summary": "展示玩过的游戏、投入时长、偏好类型和阶段性沉迷主题。",
                "items": ["RPG", "策略", "叙事冒险", "开放世界"],
                "source": "Steam API / 小黑盒同步",
            },
            {
                "title": "阅读摄入",
                "signal": "读书记录",
                "metric": "18",
                "unit": "本书",
                "summary": "沉淀今年读过的书、摘录、复盘和对个人知识图谱的影响。",
                "items": ["心理学", "哲学", "创作", "技术"],
                "source": "手动书单 / 豆瓣或微信读书导入",
            },
            {
                "title": "身体训练",
                "signal": "健身打卡",
                "metric": "34",
                "unit": "次训练",
                "summary": "记录力量、有氧、拉伸、体重趋势和身体状态的长期变化。",
                "items": ["力量", "有氧", "拉伸", "恢复"],
                "source": "运动 App / 手动打卡",
            },
        ],
        "self_hotwords": [
            {"label": "吃饭", "domain": "生活感官", "note": "记录口味偏好、餐厅地图、情绪饮食和日常能量来源。"},
            {"label": "咖啡", "domain": "生活感官", "note": "记录咖啡因、工作状态、店铺氛围和灵感触发。"},
            {"label": "夜宵", "domain": "生活感官", "note": "观察深夜欲望、社交场景和城市烟火气。"},
            {"label": "下厨", "domain": "生活感官", "note": "把菜谱、食材实验和招待朋友的经验沉淀下来。"},
            {"label": "甜品", "domain": "生活感官", "note": "记录奖励机制、审美偏好和幸福感小样本。"},
            {"label": "火锅", "domain": "生活感官", "note": "适合记录聚会关系、口味派系和社交密度。"},
            {"label": "酒精", "domain": "生活感官", "note": "记录微醺场景、边界感和情绪变化。"},
            {"label": "茶饮", "domain": "生活感官", "note": "观察轻社交、城市消费和口味周期。"},
            {"label": "零食", "domain": "生活感官", "note": "记录压力、奖励、怀旧和深夜陪伴。"},
            {"label": "早餐", "domain": "生活感官", "note": "衡量生活秩序、睡眠质量和一天的启动方式。"},
            {"label": "抽象概念", "domain": "学习认知", "note": "追踪自己对高阶概念的理解、误解和重构。"},
            {"label": "心理学", "domain": "学习认知", "note": "记录心理学学习打卡、案例、术语和自我观察。"},
            {"label": "哲学", "domain": "学习认知", "note": "把人生观、意义感和世界解释框架放进主页。"},
            {"label": "社会学", "domain": "学习认知", "note": "理解群体、阶层、制度和日常关系的运行机制。"},
            {"label": "人类学", "domain": "学习认知", "note": "记录对仪式、文化和生活方式差异的好奇。"},
            {"label": "经济学", "domain": "学习认知", "note": "观察选择、激励、成本和个人决策模式。"},
            {"label": "叙事学", "domain": "学习认知", "note": "分析故事、短片、游戏剧情和自我叙事。"},
            {"label": "认知偏差", "domain": "学习认知", "note": "记录自己容易掉进去的判断误区。"},
            {"label": "精神分析", "domain": "学习认知", "note": "适合放梦、欲望、防御机制和关系模式观察。"},
            {"label": "积极心理学", "domain": "学习认知", "note": "记录幸福感、优势、心流和长期韧性。"},
            {"label": "Steam", "domain": "游戏人格", "note": "同步游戏库、游玩时长、成就和偏好类型。"},
            {"label": "小黑盒", "domain": "游戏人格", "note": "补充国产玩家社区、动态和游戏评价记录。"},
            {"label": "RPG", "domain": "游戏人格", "note": "记录角色扮演偏好、代入感和人生选择模拟。"},
            {"label": "开放世界", "domain": "游戏人格", "note": "观察探索欲、漫游习惯和自由度需求。"},
            {"label": "策略游戏", "domain": "游戏人格", "note": "记录规划、资源调度和长期主义倾向。"},
            {"label": "独立游戏", "domain": "游戏人格", "note": "记录怪点子、机制实验和审美小众性。"},
            {"label": "恐怖游戏", "domain": "游戏人格", "note": "观察刺激阈值、恐惧偏好和安全边界。"},
            {"label": "叙事游戏", "domain": "游戏人格", "note": "记录故事冲击、选择分支和情绪余波。"},
            {"label": "多人联机", "domain": "游戏人格", "note": "观察协作、竞争、社交身份和队友关系。"},
            {"label": "成就收集", "domain": "游戏人格", "note": "衡量完成欲、收集癖和目标驱动。"},
            {"label": "读书", "domain": "阅读输入", "note": "统计读过多少书、哪些书改变了想法。"},
            {"label": "摘录", "domain": "阅读输入", "note": "沉淀值得复读的句子、概念和触发点。"},
            {"label": "书单", "domain": "阅读输入", "note": "按主题组织年度书单和待读清单。"},
            {"label": "小说", "domain": "阅读输入", "note": "记录叙事偏好、人物原型和情绪体验。"},
            {"label": "非虚构", "domain": "阅读输入", "note": "记录事实、方法、案例和世界知识。"},
            {"label": "传记", "domain": "阅读输入", "note": "从他人的人生曲线里提取策略和提醒。"},
            {"label": "诗歌", "domain": "阅读输入", "note": "保存语言敏感度、意象和不可替代的表达。"},
            {"label": "科普", "domain": "阅读输入", "note": "记录好奇心驱动下的知识扩展。"},
            {"label": "漫画", "domain": "阅读输入", "note": "记录画风、分镜、角色和轻阅读愉悦。"},
            {"label": "复盘", "domain": "阅读输入", "note": "把阅读从输入变成观点和行动。"},
            {"label": "健身", "domain": "身体状态", "note": "记录训练次数、动作、状态和身体变化。"},
            {"label": "力量训练", "domain": "身体状态", "note": "追踪重量、组数、动作技术和突破。"},
            {"label": "有氧", "domain": "身体状态", "note": "记录心肺、耐力、情绪释放和恢复情况。"},
            {"label": "跑步", "domain": "身体状态", "note": "沉淀路线、配速、天气和跑后状态。"},
            {"label": "游泳", "domain": "身体状态", "note": "记录低冲击训练、呼吸和身体放松。"},
            {"label": "骑行", "domain": "身体状态", "note": "记录城市路线、风景和耐力训练。"},
            {"label": "拉伸", "domain": "身体状态", "note": "保存恢复、柔韧和疼痛预防。"},
            {"label": "睡眠", "domain": "身体状态", "note": "记录作息、梦、恢复和第二天状态。"},
            {"label": "体重", "domain": "身体状态", "note": "与饮食、训练、压力一起观察趋势。"},
            {"label": "体态", "domain": "身体状态", "note": "记录肩颈、脊柱、核心和久坐影响。"},
            {"label": "城市漫游", "domain": "探索地图", "note": "记录城市里的路线、店铺、偶遇和灵感。"},
            {"label": "旅行", "domain": "探索地图", "note": "把目的地、照片、花费和旅途感受串起来。"},
            {"label": "展览", "domain": "探索地图", "note": "记录艺术、设计、影像和审美触发。"},
            {"label": "博物馆", "domain": "探索地图", "note": "沉淀历史、器物、文明和好奇心入口。"},
            {"label": "书店", "domain": "探索地图", "note": "记录逛书店路线、偶遇书和空间氛围。"},
            {"label": "公园", "domain": "探索地图", "note": "保存散步、观察、放空和身体恢复。"},
            {"label": "海边", "domain": "探索地图", "note": "记录开阔感、风、光线和情绪流动。"},
            {"label": "夜景", "domain": "探索地图", "note": "适合保存城市霓虹、孤独感和赛博审美。"},
            {"label": "街拍", "domain": "探索地图", "note": "记录人、物、招牌、构图和城市纹理。"},
            {"label": "路线收藏", "domain": "探索地图", "note": "把喜欢的散步路线变成可重复体验。"},
            {"label": "电影", "domain": "影像创作", "note": "记录观影、短评、镜头和主题共鸣。"},
            {"label": "短片", "domain": "影像创作", "note": "承接你自己的影视作品、实验和幕后笔记。"},
            {"label": "摄影", "domain": "影像创作", "note": "记录器材、光线、构图和照片故事。"},
            {"label": "剪辑", "domain": "影像创作", "note": "沉淀节奏、音乐、转场和叙事结构。"},
            {"label": "分镜", "domain": "影像创作", "note": "把画面想法、机位和镜头调度可视化。"},
            {"label": "配乐", "domain": "影像创作", "note": "记录音乐如何改变情绪和叙事张力。"},
            {"label": "纪录片", "domain": "影像创作", "note": "保存真实人物、现实议题和观察方法。"},
            {"label": "动画", "domain": "影像创作", "note": "记录风格、角色、运动和想象力。"},
            {"label": "剧本", "domain": "影像创作", "note": "沉淀人物、冲突、对白和结构。"},
            {"label": "幕后", "domain": "影像创作", "note": "记录拍摄过程、踩坑和团队协作。"},
            {"label": "AI工具", "domain": "工具与技术", "note": "记录常用 AI 工具、提示词和工作流。"},
            {"label": "自动化", "domain": "工具与技术", "note": "保存让生活和工作省力的小脚本。"},
            {"label": "Python", "domain": "工具与技术", "note": "记录后端、数据处理和个人工具代码。"},
            {"label": "网页", "domain": "工具与技术", "note": "沉淀这个主页自身的迭代和设计决策。"},
            {"label": "数据库", "domain": "工具与技术", "note": "记录个人数据如何存储、查询和备份。"},
            {"label": "NAS", "domain": "工具与技术", "note": "管理图片、视频、素材和长期归档。"},
            {"label": "服务器", "domain": "工具与技术", "note": "记录部署、域名、证书和服务维护。"},
            {"label": "API", "domain": "工具与技术", "note": "连接 Steam、小黑盒、阅读和运动数据。"},
            {"label": "效率系统", "domain": "工具与技术", "note": "观察待办、笔记、日程和复盘体系。"},
            {"label": "数据可视化", "domain": "工具与技术", "note": "把个人生活数据做成图表和故事。"},
            {"label": "朋友", "domain": "关系社交", "note": "记录重要关系、共同记忆和相处模式。"},
            {"label": "家人", "domain": "关系社交", "note": "保存家庭关系、责任和情感历史。"},
            {"label": "恋爱", "domain": "关系社交", "note": "观察亲密关系、边界和情绪互动。"},
            {"label": "社交局", "domain": "关系社交", "note": "记录聚会、局、聊天和社交能量。"},
            {"label": "MBTI", "domain": "关系社交", "note": "可作为趣味入口，不当成绝对标签。"},
            {"label": "ENFP", "domain": "关系社交", "note": "记录猎奇、热情、跳跃和意义驱动。"},
            {"label": "边界感", "domain": "关系社交", "note": "记录拒绝、表达、关系距离和自我保护。"},
            {"label": "表达欲", "domain": "关系社交", "note": "沉淀写作、聊天、演讲和创作冲动。"},
            {"label": "共创", "domain": "关系社交", "note": "记录和别人一起做作品、工具和项目的经验。"},
            {"label": "独处", "domain": "关系社交", "note": "观察恢复能量、思考和自我连接。"},
            {"label": "穿搭", "domain": "审美消费", "note": "记录风格变化、颜色偏好和身份表达。"},
            {"label": "香水", "domain": "审美消费", "note": "记录气味、记忆和自我氛围。"},
            {"label": "数码", "domain": "审美消费", "note": "记录设备、工具、折腾和消费判断。"},
            {"label": "桌面", "domain": "审美消费", "note": "保存工作台、灯光、摆件和效率氛围。"},
            {"label": "房间", "domain": "审美消费", "note": "记录居住空间、收纳和情绪环境。"},
            {"label": "赛博朋克", "domain": "审美消费", "note": "沉淀霓虹、玻璃、夜色和未来感审美。"},
            {"label": "复古", "domain": "审美消费", "note": "记录旧物、胶片感和怀旧偏好。"},
            {"label": "极简", "domain": "审美消费", "note": "记录少即是多、清爽界面和生活减负。"},
            {"label": "玩具", "domain": "审美消费", "note": "保存模型、手办、摆件和童心。"},
            {"label": "消费复盘", "domain": "审美消费", "note": "判断什么东西真的提升了生活质量。"},
            {"label": "梦", "domain": "内在宇宙", "note": "记录梦境、象征、情绪和潜意识片段。"},
            {"label": "情绪", "domain": "内在宇宙", "note": "追踪开心、低落、焦虑、兴奋和触发源。"},
            {"label": "灵感", "domain": "内在宇宙", "note": "把突然冒出来的点子快速保存。"},
            {"label": "欲望", "domain": "内在宇宙", "note": "观察想要什么、为什么想要、是否值得追。"},
            {"label": "意义感", "domain": "内在宇宙", "note": "把重要问题放在主页长期追问。"},
            {"label": "人生节点", "domain": "内在宇宙", "note": "记录关键选择、转折、告别和开始。"},
            {"label": "失败样本", "domain": "内在宇宙", "note": "把失败转化成可复用的经验。"},
            {"label": "高光时刻", "domain": "内在宇宙", "note": "保存值得反复确认的自我证据。"},
            {"label": "怪知识", "domain": "内在宇宙", "note": "ENFP 式随机好奇心收纳箱。"},
            {"label": "人生实验", "domain": "内在宇宙", "note": "把生活当作可观察、可调整的实验场。"},
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
