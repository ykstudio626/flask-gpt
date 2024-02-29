# ベースイメージの指定
FROM python:3.11.6

# コンテナ内にコードを格納するディレクトリを作成し、ここをルートとする
WORKDIR /app

# ローカルの/app内の内容をコンテナにコピー
COPY ./app /app

# pipをアップデート
RUN pip install --upgrade pip

# 必要最低限のライブラリをインストール
RUN pip install -r requirements.txt

# 起動コマンド
ENTRYPOINT [ "python", "app.py" ]