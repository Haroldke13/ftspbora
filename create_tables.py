import os
from app import app
from models import db

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dailytracking_db.sqlite')

if __name__ == "__main__":
    # Remove the existing SQLite database file if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database deleted.")
    with app.app_context():
        db.create_all()
        print("All tables created successfully.")
