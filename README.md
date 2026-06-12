# 你的人生学无限

这是一个面向长期使用的个人主页系统，用于归档学习总结、wiki、思考文章、自用小工具、个人介绍、生活日记、关键事件时间线、微信/支付宝打赏入口，以及个人影视作品记录。

项目首版使用 Python + FastAPI + SQLAlchemy，可接 Postgres。图片和视频封面等媒体文件通过 `MEDIA_ROOT` 指向服务器上的 NFS/NAS 挂载目录。

## 功能骨架

- 学习总结、wiki、思考文章目录
- `public` / `member` / `private` 三种内容可见性
- 游客评论、会员共创、关闭评论三种评论策略
- 自用工具空间和维护状态
- 关于我模块
- 生活日记
- 关键事件快速记录和时间线回溯
- 微信、支付宝打赏二维码配置位
- 影视作品记录，并支持引用相关 wiki 或文章
- 媒体上传接口，适配 NFS/NAS 存储目录

## 本地运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn personal_homepage.main:app --reload
```

打开 `http://127.0.0.1:8000`。

没有配置 `DATABASE_URL` 时，开发环境会使用 `data/dev.db`。部署到服务器时建议使用 Postgres：

```env
DATABASE_URL=postgresql+psycopg://homepage:change-me@127.0.0.1:5432/homepage
MEDIA_ROOT=/mnt/nas/homepage-media
PUBLIC_MEDIA_URL=/media
AUTO_SEED=true
```

## Docker Compose

```bash
docker compose up --build
```

默认会启动：

- `web`: FastAPI 应用
- `postgres`: Postgres 16

部署到真实服务器时，可以把 `docker-compose.yml` 里的 `./media` 替换成你的 NFS/NAS 挂载路径，例如 `/mnt/nas/homepage-media:/app/media`。

## 重要路径

- 页面模板：`personal_homepage/templates/index.html`
- 静态样式：`personal_homepage/static/styles.css`
- 前端交互：`personal_homepage/static/app.js`
- 数据模型：`personal_homepage/models.py`
- 初始数据：`personal_homepage/seed.py`
- 媒体目录：由 `MEDIA_ROOT` 控制

## 下一步建议

- 接入真实登录和会员系统
- 把 Markdown 正文渲染、全文搜索和标签页做完整
- 给评论增加审核、反垃圾和通知
- 影视作品支持视频源、剧照、幕后 wiki 和授权说明
