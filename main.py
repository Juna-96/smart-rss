import os
import httpx
from fastapi import FastAPI
from feedgen.feed import FeedGenerator
from pydantic import BaseModel

# 配置
WEWE_RSS_URL = "https://your-wewe-rss-url/all.json"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

app = FastAPI()


class Article(BaseModel):
    title: str
    link: str
    content: str
    source: str


# -------------------------------
# 调用 DeepSeek API
# -------------------------------
async def call_deepseek(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


# -------------------------------
# 分类：通知类 vs 信息类
# -------------------------------
async def classify_article(article: Article) -> str:
    prompt = f"""
请判断以下文章是否为“活动招募、讲座、报名”类型的通知，而不是商业推广或举办活动之后的宣传稿。
只回答 保留 或 丢弃。

标题: {article.title}
内容: {article.content[:500]}
"""
    return await call_deepseek(prompt)


# -------------------------------
# 信息类摘要
# -------------------------------
async def summarize_article(article: Article) -> str:
    prompt = f"""
为以下文章生成简洁摘要，不超过150字：
{article.content}
"""
    return await call_deepseek(prompt)


# -------------------------------
# 获取 WeWe RSS -> 处理 -> 输出新RSS
# -------------------------------
@app.get("/smart-rss.xml")
async def generate_smart_rss():
    async with httpx.AsyncClient() as client:
        resp = await client.get(WEWE_RSS_URL, timeout=60)
        articles = resp.json()

    fg = FeedGenerator()
    fg.title("Smart RSS (Powered by DeepSeek)")
    fg.link(href="http://example.com")
    fg.description("过滤 & 摘要后的 RSS 源")

    filtered_articles = []

    for a in articles:
        article = Article(
            title=a.get("title", ""),
            link=a.get("link", ""),
            content=a.get("content", ""),
            source=a.get("source", "")
        )

        # 假设 "通知类" 来自特定公众号
        if article.source in ["公众号A", "公众号B"]:
            decision = await classify_article(article)
            if decision == "保留":
                filtered_articles.append(article)
        else:
            # 信息类：生成摘要
            summary = await summarize_article(article)
            article.content = summary
            filtered_articles.append(article)

    # 构造新 RSS
    for art in filtered_articles:
        fe = fg.add_entry()
        fe.title(art.title)
        fe.link(href=art.link)
        fe.description(art.content)

    return fg.rss_str(pretty=True)
