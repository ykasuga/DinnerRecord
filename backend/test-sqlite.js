const sqlite3 = require('sqlite3').verbose();

// ローカルファイルにデータベースを作成
const db = new sqlite3.Database('./test.db'); // meals.dbにデータを保存

// データベーステーブル作成（もしテーブルが存在しない場合）
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, date TEXT, menu TEXT)");
  db.run("INSERT INTO test (date, menu) VALUES ('2020-01-01', 'カレー')");
});

db.close();
