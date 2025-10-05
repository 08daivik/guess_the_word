

# 🧩 Guess The Word — Flask Web App

A fun and interactive **Word Guessing Game** built using **Python (Flask)**, **HTML**, **CSS**, and **JavaScript** — with user authentication, admin reporting, and persistent database storage.

Players try to guess a random word, and the app provides feedback similar to Wordle-style hints (correct letter, position, etc.).

---

## 🚀 Features

### 👥 User Features

* Register and login securely.
* Play the Guess-The-Word game with color feedback.
* View personalized gameplay and results.

### 🧑‍💼 Admin Features

* Dedicated **Admin Dashboard** to view reports:

  * **Daily Report:** number of users played, correct guesses, and usernames.
  * **User Report:** list of words tried, correct guesses per date.
* Role-based access (admin vs player).

### 💾 Data Persistence

* Words, guesses, and results stored in **SQLite** (or optional **MySQL**) database.
* Tracks:

  * Given word
  * User’s guesses
  * Correct answers
  * Date and time of each game

---

## 🛠️ Tech Stack

| Component      | Technology                                       |
| -------------- | ------------------------------------------------ |
| Frontend       | HTML, CSS, JavaScript (Bootstrap 5)              |
| Backend        | Flask (Python)                                   |
| Database       | SQLite (default) or MySQL (optional)             |
| ORM            | SQLAlchemy                                       |
| Authentication | Flask-Login                                      |
| Reports        | Flask routes returning JSON + rendered templates |

---

## 📂 Project Structure

```
Guess the word/
│
├── app.py                # Main Flask app
├── seed_words.py         # Seeds initial data (words + admin user)
├── requirements.txt      # Python dependencies
├── instance/
│   └── app.db            # SQLite database (auto-created)
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── play.html
│   └── admin_report.html
│
├── static/
│   └── js/
│       └── game.js       # Game logic (word matching, feedback)
│
└── README.md             # This file
```

---

## ⚙️ Installation and Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<08daivik>/guess_the_word.git
cd guess_the_word
```

---

### 2️⃣ Create and Activate Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Database Setup (SQLite — Default)

SQLite database is automatically created in the `instance/` folder when you run the app.
To seed initial data (words + admin user):

```bash
python seed_words.py
```

Default admin credentials:

```
Username: admin
Password: Admin@123
```

---

### 5️⃣ (Optional) Switch to MySQL

If you prefer MySQL instead of SQLite:

1. Install connector:

   ```bash
   pip install pymysql
   ```
2. Create a MySQL database:

   ```sql
   CREATE DATABASE guess_the_word;
   ```
3. Update your `app.py`:

   ```python
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/guess_the_word'
   ```
4. Run:

   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   python seed_words.py
   ```

---

### 6️⃣ Run the Application

```bash
flask run
```

or

```bash
python app.py
```

App runs locally at:
👉 **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🧠 Admin Dashboard

Access the admin panel after logging in as admin:
👉 [http://127.0.0.1:5000/admin/dashboard](http://127.0.0.1:5000/admin/dashboard)

You can:

* Fetch **Daily Reports** (`/admin/report/day?date=YYYY-MM-DD`)
* Fetch **User Reports** (`/admin/report/user?username=USERNAME`)

---

## 📊 Database Schema Overview

### 🧱 Tables

| Table   | Purpose                                                   |
| ------- | --------------------------------------------------------- |
| `user`  | Stores users, hashed passwords, and role info             |
| `word`  | Stores all playable words                                 |
| `game`  | Stores each game session (user_id, word_id, solved, date) |
| `guess` | Stores each guess (game_id, text, feedback, timestamp)    |

---

## 🎮 Gameplay Logic (Summary)

* A random word is selected from the `word` table.
* User guesses words.
* Each letter is compared with the target word:

  * 🟩 Green — correct letter in correct position
  * 🟧 Orange — correct letter in wrong position
  * ⬜ Grey — incorrect letter
* All guesses are stored in the database with timestamps.

---

## 🧰 Common Commands

| Command                           | Description                        |
| --------------------------------- | ---------------------------------- |
| `pip install -r requirements.txt` | Install all dependencies           |
| `python seed_words.py`            | Seed database with words and admin |
| `flask run`                       | Start the development server       |
| `sqlite3 instance/app.db`         | Inspect SQLite database manually   |
| `python` + `from app import db`   | Access SQLAlchemy database object  |

---

## 🧾 Admin Credentials

| Username | Password    |
| -------- | ----------- |
| `admin`  | `Admin@123` |

---


## 🧑‍💻 Developer Notes

* Works best on Python 3.10+
* Tested on Windows 10 / 11 and macOS
* For MySQL version, ensure `pymysql` is installed.
* You can view the database directly at:

  ```
  instance/app.db
  ```

---

## 🪪 License

This project is open-source and available under the **MIT License**.

---

## 📧 Author

**Developed by:** Daivik S M



