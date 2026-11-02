import os

from flask import Flask
from flask_login import LoginManager
from .models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "kunci-rahasia-website-desa"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(app.instance_path, "desa.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads"
    )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"

    from .routes import main
    from .auth import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()
        user = User.query.filter_by(username="admin").first()
        if not user:
            from werkzeug.security import generate_password_hash
            user = User(
                username="admin",
                password=generate_password_hash("admin123")
            )
            db.session.add(user)
            db.session.commit()
    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))