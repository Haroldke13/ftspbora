from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from routes import routes


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(routes)


# Create Flask-Migrate object for migrations
migrate = Migrate(app, db)
# Create Mail object for sending emails
mail = Mail(app)
# Create OAuth object for external login
oauth = OAuth(app)

if __name__ == "__main__":
    # For local dev only; production uses gunicorn
    app.run(host="0.0.0.0", port=10000)
