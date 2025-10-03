import os
import httpx
from fastapi import FastAPI
from feedgen.feed import FeedGenerator
from pydantic import BaseModel

# 配置
WEWE_RSS_URL = os.getenv("WEWE_RSS_URL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

app = FastAPI()

# 定义文章数据结构
class Article(BaseModel):
    title: str
    link: str
    content: str
    source: str

# 根路由提示
@app.get("/")
async def root():
    return {"message": "Smart-RSS is running! Try /smart-rss.xml"}

# 输出 RSS
@app.get("/smart-rss.xml")
async def generate_smart_rss():
    async with httpx.AsyncClient() as client:
        resp = await client.get(WEWE_RSS_URL, timeout=60)
        feed = resp.json()

    items = feed.get("items", [])
    fg = FeedGenerator()
    fg.title("Smart RSS (Basic Mode)")
    fg.link(href="http://example.com")
    fg.description("过滤 & 摘要后的 RSS 源")

    for a in items:
        article = Article(
            title=a.get("title", ""),
            link=a.get("url", ""),
            content=a.get("content_html", "") or "请点击链接查看原文",
            source=a.get("author", {}).get("name", "")
        )

        fe = fg.add_entry()
        fe.title(article.title)
        fe.link(href=article.link)
        fe.description(article.content)

    return fg.rss_str(pretty=True)
