# Python 3の公式イメージを使用
FROM python:3.12

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonパッケージをインストール
COPY requirements.txt ./
RUN pip install -r requirements.txt

# ソースコードをコンテナにコピー
COPY . .

# Streamlitアプリを実行するポートを公開
EXPOSE 8501

# Streamlitアプリを実行
# CMD ["streamlit", "run", "app.py"]
CMD ["bash"]
