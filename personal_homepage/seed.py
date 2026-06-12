from datetime import date

from sqlalchemy.orm import Session

from .models import ContentItem, FilmWork, JournalEntry, TimelineEvent, ToolItem


def seed_database(db: Session) -> None:
    if db.query(ContentItem).first():
        return

    db.add_all(
        [
            ContentItem(
                slug="learning-system",
                kind="wiki",
                title="个人学习系统搭建笔记",
                summary="记录如何把阅读、课程、实践项目拆成 wiki、总结和复盘文章。",
                body="这里后续可以放 Markdown 正文，或接入独立文章编辑器。",
                visibility="public",
                comment_policy="visitor",
                tags=["学习方法", "知识管理", "wiki"],
                published_at=date(2026, 6, 13),
            ),
            ContentItem(
                slug="creator-workflow",
                kind="wiki",
                title="影视创作流程 Wiki",
                summary="从选题、脚本、分镜、拍摄、剪辑到发布的完整流程索引。",
                body="后续影视作品可以引用这里的流程节点和指导文章。",
                visibility="member",
                comment_policy="member",
                tags=["影视", "创作", "工作流"],
                published_at=date(2026, 6, 12),
            ),
            ContentItem(
                slug="private-review",
                kind="article",
                title="年度私密复盘",
                summary="只保留给自己看的关键选择、情绪变化和下一步策略。",
                body="私密内容默认不应对游客开放。",
                visibility="private",
                comment_policy="closed",
                tags=["复盘", "私密", "人生设计"],
                published_at=date(2026, 6, 1),
            ),
            ContentItem(
                slug="tool-thinking",
                kind="article",
                title="小工具产品判断清单",
                summary="判断一个个人工具是否值得继续维护：频率、节省时间、数据价值。",
                body="可以作为工具空间每个项目的复盘模板。",
                visibility="public",
                comment_policy="visitor",
                tags=["工具", "产品", "效率"],
                published_at=date(2026, 5, 28),
            ),
        ]
    )

    db.add_all(
        [
            ToolItem(
                name="灵感速记器",
                status="自用中",
                description="快速记录一个想法，并自动归档到学习、创作或生活主题。",
                tags=["记录", "本地存储"],
            ),
            ToolItem(
                name="文章目录生成器",
                status="维护中",
                description="把 markdown 标题整理成 wiki 目录，方便长文和系列文章导航。",
                tags=["写作", "知识库"],
            ),
            ToolItem(
                name="作品引用检查器",
                status="计划中",
                description="检查影视作品页面引用了哪些 wiki、文章和素材说明。",
                tags=["影视", "引用"],
            ),
        ]
    )

    db.add_all(
        [
            JournalEntry(
                title="主页项目启动",
                body="把个人主页定位为知识、工具、生活、事件、作品共同生长的地方。",
                visibility="public",
                written_at=date(2026, 6, 13),
            ),
            JournalEntry(
                title="整理近期学习主题",
                body="把零散笔记拆成公开文章、会员讨论和私密复盘三类。",
                visibility="private",
                written_at=date(2026, 6, 8),
            ),
        ]
    )

    db.add_all(
        [
            TimelineEvent(
                title="个人主页第一版",
                event_type="创作",
                note="完成知识归档、工具空间、日记、时间线、打赏和作品记录的基础结构。",
                happened_at=date(2026, 6, 13),
                visibility="public",
            ),
            TimelineEvent(
                title="确认内容权限模型",
                event_type="学习",
                note="公开给所有人，会员可参与，私密只做自我回顾。",
                happened_at=date(2026, 6, 12),
            ),
            TimelineEvent(
                title="建立月度复盘习惯",
                event_type="生活",
                note="每月保留一个关键复盘节点，用于回看生活和创作节奏。",
                happened_at=date(2026, 6, 1),
            ),
        ]
    )

    db.add_all(
        [
            FilmWork(
                title="短片项目 A",
                year="2026",
                role="策划 / 剪辑",
                summary="一个关于学习路径与人生选择的短片占位记录。",
                references=["影视创作流程 Wiki", "个人学习系统搭建笔记"],
            ),
            FilmWork(
                title="纪录片片段 B",
                year="2025",
                role="拍摄 / 后期",
                summary="用于记录真实生活片段，也会引用生活日记和关键事件。",
                references=["年度私密复盘"],
                visibility="private",
            ),
        ]
    )

    db.commit()
