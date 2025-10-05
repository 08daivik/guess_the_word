from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import random, json, os
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("Using database:", os.path.abspath(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')))
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ----------------------------- Models -----------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5), unique=True, nullable=False)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    word_id = db.Column(db.Integer, db.ForeignKey('word.id'))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    guesses = db.Column(db.Integer, default=0)
    solved = db.Column(db.Boolean, default=False)


class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    text = db.Column(db.String(5), nullable=False)
    feedback = db.Column(db.String(50))  # e.g. "GOGGG"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -------------------------- Login loader ---------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --------------------------- Validators ----------------------------
def valid_username(username):
    if not username or len(username) < 5:
        return False
    return any(c.islower() for c in username) and any(c.isupper() for c in username)


def valid_password(password):
    if not password or len(password) < 5:
        return False
    specials = set('$%*@')
    return any(c.isalpha() for c in password) and any(c.isdigit() for c in password) and any(c in specials for c in password)


# ------------------------- Helper logic ---------------------------
def feedback_for(secret, guess):
    secret = secret.upper()
    guess = guess.upper()
    res = ['grey'] * 5
    remaining = {}
    for i, ch in enumerate(secret):
        if guess[i] == ch:
            res[i] = 'green'
        else:
            remaining[ch] = remaining.get(ch, 0) + 1
    for i, ch in enumerate(guess):
        if res[i] == 'grey' and remaining.get(ch, 0) > 0:
            res[i] = 'orange'
            remaining[ch] -= 1
    return res


def encode_feedback(feedback_list):
    m = {'green': 'G', 'orange': 'O', 'grey': 'X'}
    return ''.join(m[x] for x in feedback_list)


# ---------------------------- Routes ------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -------------------------- Register -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not valid_username(username):
            flash('Username must be at least 5 chars and contain both UPPER and lower case.', 'danger')
            return redirect(url_for('register'))
        if not valid_password(password):
            flash('Password must be at least 5 chars and contain letters, numbers and one of $ % * @', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


# --------------------------- Login -------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('play_page'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


# --------------------------- Game Routes --------------------------
@app.route('/play')
@login_required
def play_page():
    if current_user.is_admin:
        flash('Admins cannot play the game.', 'warning')
        return redirect(url_for('admin_dashboard'))
    return render_template('play.html')


@app.route('/play/start', methods=['POST'])
@login_required
def start_game():
    today = date.today()
    games_today = Game.query.filter(
        Game.user_id == current_user.id,
        db.func.date(Game.started_at) == today
    ).count()
    if games_today >= 3:
        return jsonify({'ok': False, 'msg': 'Maximum of 3 games per day reached.'}), 400
    word = Word.query.order_by(db.func.random()).first()
    if not word:
        return jsonify({'ok': False, 'msg': 'No words seeded.'}), 500
    game = Game(user_id=current_user.id, word_id=word.id)
    db.session.add(game)
    db.session.commit()
    return jsonify({'ok': True, 'game_id': game.id, 'msg': 'Game started'}), 201


@app.route('/play/guess', methods=['POST'])
@login_required
def submit_guess():
    data = request.json or {}
    game_id = data.get('game_id')
    guess_text = (data.get('guess') or '').strip().upper()
    if len(guess_text) != 5 or not guess_text.isalpha():
        return jsonify({'ok': False, 'msg': 'Guess must be a 5-letter word.'}), 400
    game = Game.query.get(game_id)
    if not game or game.user_id != current_user.id:
        return jsonify({'ok': False, 'msg': 'Game not found.'}), 404
    if game.solved or game.guesses >= 5:
        return jsonify({'ok': False, 'msg': 'Game already finished.'}), 400
    word = Word.query.get(game.word_id)
    fb = feedback_for(word.text, guess_text)
    enc = encode_feedback(fb)
    g = Guess(game_id=game.id, text=guess_text, feedback=enc)
    db.session.add(g)
    game.guesses += 1
    if guess_text == word.text:
        game.solved = True
    db.session.commit()
    status = 'continue'
    if game.solved:
        status = 'won'
    elif game.guesses >= 5:
        status = 'lost'
    return jsonify({'ok': True, 'feedback': fb, 'encoded': enc, 'status': status, 'guesses_used': game.guesses})


# --------------------------- Admin Routes -------------------------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: Admins only', 'danger')
        return redirect(url_for('index'))
    return render_template('admin_report.html')


@app.route('/admin/report/day')
@login_required
def admin_day_report():
    if not current_user.is_admin:
        return jsonify({'ok': False, 'msg': 'Admin only'}), 403

    qdate = request.args.get('date')
    if not qdate:
        return jsonify({'ok': False, 'msg': 'Please provide date=YYYY-MM-DD'}), 400
    try:
        d = datetime.strptime(qdate, '%Y-%m-%d').date()
    except:
        return jsonify({'ok': False, 'msg': 'Invalid date format'}), 400

    games = Game.query.filter(db.func.date(Game.started_at) == d).all()
    user_ids = {g.user_id for g in games}

    usernames = []
    if user_ids:
        usernames = [u.username for u in User.query.filter(User.id.in_(user_ids)).all()]

    correct_guesses = (
        db.session.query(Guess)
        .join(Game, Guess.game_id == Game.id)
        .filter(db.func.date(Guess.created_at) == d, Game.solved == True)
        .count()
    )

    return jsonify({
        'ok': True,
        'date': qdate,
        'users_played': len(user_ids),
        'usernames': usernames,
        'correct_guesses': correct_guesses
    })


@app.route('/admin/report/user')
@login_required
def admin_user_report():
    if not current_user.is_admin:
        return jsonify({'ok': False, 'msg': 'Admin only'}), 403
    username = request.args.get('username')
    if not username:
        return jsonify({'ok': False, 'msg': 'Provide username param'}), 400
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'ok': False, 'msg': 'User not found'}), 404
    rows = db.session.execute(db.text("""
        SELECT date(g.started_at) as d, count(g.id) as words_tried,
        sum(case when g.solved then 1 else 0 end) as correct
        FROM game g WHERE g.user_id = :uid
        GROUP BY date(g.started_at)
        ORDER BY d DESC
    """), {'uid': user.id}).fetchall()
    result = [{'date': str(r[0]), 'words_tried': r[1], 'correct': r[2]} for r in rows]
    return jsonify({'ok': True, 'username': username, 'report': result})


# --------------------------- Run App ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
