# Pythonイメージを基に作成
FROM python:3.9

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# コンテナ起動時にアプリケーションを実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
