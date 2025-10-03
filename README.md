# Smart RSS (with DeepSeek AI)

一个智能 RSS 中转服务：
- 过滤通知类推广，只保留活动/讲座/报名类通知
- 信息类文章自动生成摘要

## 部署
### 本地运行
```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="your_api_key"
uvicorn main:app --reload --port 8000
