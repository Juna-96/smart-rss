FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制项目文件
COPY . .

# 启动服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
