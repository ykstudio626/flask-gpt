from flask import Flask, request, jsonify, render_template, session, stream_with_context
from datetime import timedelta #時間情報を用いるため
import flask
import json
import os
from openai import OpenAI
import logging
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

client = OpenAI()

dbclient = MongoClient(
    host = 'mongodb',
    port = 27017,
    username = os.environ.get('MONGO_USERNAME'),
    password = os.environ.get('MONGO_PASSWORD'),
    authSource = 'chat',
)
db = dbclient.chat


@app.route('/')
def index():
    return '<h2>Top</h2><a href="/ask">ChatGPTを開始する</a>'


@app.route('/ask', methods=['POST','GET'])
def ask():

    openai_model = "gpt-3.5-turbo"
    
    question = request.args.get("question","")
    question = str(question).strip()

    # 新しい質問
    question_obj = {"role": "user", "content": question}

    # DBに保存
    db.messages.insert_one(question_obj)

    # DBから過去の質問と回答を取得する
    messages_past = db.messages.find().sort("_id",-1).limit(5) # 質問3件 + 回答2件

    # messageの組み立て
    messages = []

    for m in messages_past: 
        del m["_id"] # 不要なキーを削除
        messages.insert(0, m) # 最後の質問が一番最後に来るように先頭に挿入

    system_obj = {"role": "system", "content": "You are a helpful assistant."}
    messages.insert(0, system_obj)

    # 質問が送られてきたら
    if question:
        def stream():
            """
            ストリーム関数（戻り値はgenerator: 回答を逐次生成する）
            """

            app.logger.info("sent messages:")
            app.logger.info(messages)

            result = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                stream=True
            )

            answer = ""

            for trunk in result:
                if trunk.choices[0].finish_reason == 'stop': # 回答が終了した
                    data = '[DONE]'
                    
                else:
                    data = trunk.choices[0].delta.content
                    answer += data
                    data = data.replace("\n", "<br>") # ブラウザ上では改行は認識されないのでタグに変換
                yield "data: %s\n\n" % data

            if answer:
                answer_obj = {"role": "assistant", "content": answer}
                
                # 回答をDBに保存
                db.messages.insert_one(answer_obj)
            
        return flask.Response(stream_with_context(stream()), mimetype="text/event-stream")

    # 質問がない場合は、フォームを表示
    return render_template('index.html')
        
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)