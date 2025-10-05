from app import app, db, User, Word
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():   # ✅ ensures we're inside Flask app context
        db.create_all()

        # seed 20 five-letter words (uppercase)
        words = [
            "APPLE", "BERRY", "CHAIR", "TABLE", "WORLD", "HAPPY", "SNAKE", "TIGER",
            "HOUSE", "RIVER", "LIGHT", "BLANK", "SHIFT", "NIGHT", "MOUSE", "DREAM",
            "PLANT", "SHEEP", "FRAME", "LEMON"
        ]
        for w in words:
            if not Word.query.filter_by(text=w).first():
                db.session.add(Word(text=w))

        # create an admin user for convenience
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', is_admin=True)
            admin.password_hash = generate_password_hash('Admin@123')
            db.session.add(admin)

        db.session.commit()
        print('✅ Seeded database with words and admin user.')

if __name__ == '__main__':
    seed()
