# backend ディレクトリに Dockerfile を作成
FROM python:3.11-slim

WORKDIR /app

# 依存ファイルをコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# ソースコードをコピー
COPY . .

# FastAPI ポートと WebSocket ポートを公開
EXPOSE 8000

# FastAPI アプリケーションを起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]