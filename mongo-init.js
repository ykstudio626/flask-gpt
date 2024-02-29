// 新しいDBを作成
db = db.getSiblingDB('chat');

// 新しいDBにアクセスするユーザを作成
db.createUser({
    user: "chatuser", 
    pwd: "password", 
    roles: [
        {
            role:"readWrite",
            db: "chat"
        }
    ]})

// コレクション（テーブル）を作成
db.createCollection('messages');
