const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');

const app = express();

// ローカルファイルにデータベースを作成
const db = new sqlite3.Database('./meals.db'); // meals.dbにデータを保存

app.use(bodyParser.json());

// データベーステーブル作成（もしテーブルが存在しない場合）
db.serialize(() => {
  db.run("CREATE TABLE IF NOT EXISTS menu_list (id INTEGER PRIMARY KEY, menu TEXT NOT NULL UNIQUE)");
  db.run("CREATE TABLE IF NOT EXISTS dinner_log (date DATE NOT NULL, menu_order INTEGER NOT NULL, menu_id INTEGER NOT NULL, PRIMARY KEY(date, menu_order), FOREIGN KEY(menu_id) REFERENCES menu_list(id))");
});

// Middleware to handle errors
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

// 晩御飯メニューを記録するAPI
app.post('/add-meal', (req, res) => {
  const { date, menu } = req.body;
  db.serialize(() => {
    db.run("INSERT OR IGNORE INTO menu_list (menu) VALUES (?)", [menu], function(err) {
      if (err) {
        return res.status(500).send(err.message);
      }
      const menu_id = this.lastID;
      db.get("SELECT id FROM menu_list WHERE menu = ?", [menu], (err, row) => {
        if (err) {
          return res.status(500).send(err.message);
        }
        const menu_id = row.id;
        db.get("SELECT COUNT(*) AS count FROM dinner_log WHERE date = ?", [date], (err, row) => {
          if (err) {
            return res.status(500).send(err.message);
          }
          const menu_order = row.count + 1;
          db.run("INSERT INTO dinner_log (date, menu_order, menu_id) VALUES (?, ?, ?)", [date, menu_order, menu_id], function(err) {
            if (err) {
              return res.status(500).send(err.message);
            }
            res.status(200).send({ id: this.lastID });
          });
        });
      });
    });
  });
});

// 特定の日付のメニューを取得するAPI
app.get('/get-meals/:date', (req, res) => {
  const { date } = req.params;
  db.all("SELECT dl.date, dl.menu_order, ml.menu FROM dinner_log dl JOIN menu_list ml ON dl.menu_id = ml.id WHERE dl.date = ? ORDER BY dl.menu_order", [date], (err, rows) => {
    if (err) {
      return res.status(500).send(err.message);
    }
    res.status(200).json(rows);
  });
});

// 一週間分の記録を取得
app.get('/meals-week', (req, res) => {
  const { startDate } = req.query;

  if (!startDate) {
    return res.status(400).json({ error: 'Missing startDate' });
  }

  // 一週間分の日付範囲を計算
  const endDate = new Date(startDate);
  endDate.setDate(endDate.getDate() + 6);
  const endDateStr = endDate.toISOString().split('T')[0];

  // 一週間分の記録を取得
  db.all("SELECT dl.date, dl.menu_order, ml.menu FROM dinner_log dl JOIN menu_list ml ON dl.menu_id = ml.id WHERE dl.date BETWEEN ? AND ? ORDER BY dl.date, dl.menu_order", [startDate, endDateStr], (err, rows) => {
    if (err) {
      console.error('Database error:', err.message);
      return res.status(500).json({ error: 'Failed to fetch meals' });
    }

    res.json({ meals: rows });
  });
});

// 特定のメニューが記録された日付を取得するAPI
app.get('/get-dates/:menu', (req, res) => {
  const { menu } = req.params;
  db.all("SELECT dl.date FROM dinner_log dl JOIN menu_list ml ON dl.menu_id = ml.id WHERE ml.menu LIKE ?", [`%${menu}%`], (err, rows) => {
    if (err) {
      return res.status(500).send(err.message);
    }
    res.status(200).json(rows);
  });
});

app.get('/all-meals', (req, res) => {
  db.all("SELECT DISTINCT menu FROM menu_list ORDER BY menu ASC", (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch meals' });
    }
    res.json({ meals: rows });
  });
});

// 日付を指定してその日のメニューを削除
app.delete('/delete-meals', (req, res) => {
  const { date } = req.body;

  // 日付の入力チェック
  if (!date) {
    return res.status(400).json({ error: 'Date is required' });
  }

  // データベースから削除
  db.run("DELETE FROM dinner_log WHERE date = ?", [date], (err) => {
    if (err) {
      console.error('Database error:', err.message);
      return res.status(500).json({ error: 'Failed to delete meals' });
    }

    res.json({ success: true });
  });
});

app.get('/menu-counts', (req, res) => {
  db.all("SELECT ml.menu, COUNT(dl.menu_id) as count FROM dinner_log dl JOIN menu_list ml ON dl.menu_id = ml.id GROUP BY ml.menu ORDER BY count DESC", (err, rows) => {
    if (err) {
      return res.status(500).json({ error: 'Failed to fetch menu counts' });
    }
    res.status(200).json({ menu_counts: rows });
  });
});

// Close the database connection when the server is shutting down
process.on('SIGINT', () => {
  db.close((err) => {
    if (err) {
      console.error('Failed to close the database:', err.message);
    } else {
      console.log('Database connection closed.');
    }
    process.exit(0);
  });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
