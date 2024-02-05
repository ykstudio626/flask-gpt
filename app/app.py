from flask import Flask, request, jsonify, render_template, session
from datetime import timedelta #時間情報を用いるため
import flask
import json
from openai import OpenAI
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = 'chatgpt'
app.permanent_session_lifetime = timedelta(minutes=15)

client = OpenAI()

@app.route('/')
def index():
    return '<h2>Top</h2>'


@app.route('/ask', methods=['POST','GET'])
def ask():

    openai_model = "gpt-3.5-turbo"
    
    question = request.args.get("question","")
    question = str(question).strip()

    session.permanent = True

    app.logger.info("question=")
    app.logger.info(question)

    # 質問が送られてきたら
    if question:

        # セッションに過去のメッセージがないかどうかチェックする
        _messages = session.get("messages", "")

        if _messages == "": # もしなければ、初期メッセージを作成
            messages = [{"role": "system", "content": "You are a helpful assistant."}]
        else: # もしあれば、jsonからデータに変換する
            messages = json.loads(_messages)

        # 新しいメッセージを組み立てる
        message_unit = {"role": "user", "content": question}

        # 古いメッセージと合成
        messages.append(message_unit)
        messages = messages[-5:] # 最後の5メッセージのみを取り出す

        # セッションに保存する
        session["messages"] = json.dumps(messages)
        
        def stream():

            app.logger.info("messages=")
            app.logger.info(messages)

            result = client.chat.completions.create(
                model=openai_model,
                messages=messages,
                stream=True
            )

            for trunk in result:
                if trunk.choices[0].finish_reason == 'stop': # 回答が終了した
                    data = '[DONE]'
                else:
                    data = trunk.choices[0].delta.content
                    data = data.replace("\n", "<br>") # ブラウザ上では改行は認識されないのでタグに変換
                    
                yield "data: %s\n\n" % data

        return flask.Response(stream(), mimetype="text/event-stream")

    # 質問がない場合は、フォームを表示
    return render_template('index.html')
        

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)