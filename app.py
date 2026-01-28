from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from models import db

mail = Mail()

def create_app():
    app = Flask(__name__)
    # config
    app.config.from_object("config.Config")

    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)
    oauth = OAuth(app)

    from routes import routes
    app.register_blueprint(routes)

    return app

app = create_app()

if __name__ == "__main__":
    # For local dev only; production uses gunicorn
    app.run(host="0.0.0.0", port=10000)
