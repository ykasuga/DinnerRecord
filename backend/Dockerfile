# Node.jsの公式イメージを使用
FROM node:16

# 作業ディレクトリを設定
WORKDIR /app

# package.json と package-lock.json をコピー
COPY package.json package-lock.json ./

# 必要なパッケージをインストール
RUN npm install \
    && npm install nodemon -g \
    && npm install express

# ソースコードをコンテナにコピー
COPY . .

# サーバーを起動するポートを公開
EXPOSE 3000

# サーバーを起動
# CMD ["nodemon", "server.js"]
CMD ["bash"]
