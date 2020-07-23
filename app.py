import os

from flask import Flask
from flask_login import LoginManager

import auth
import main
from src.db.db_utils import User, DbUtil


def create_app() -> Flask:
    """Construct the core app object."""
    app = Flask(__name__)

    app.config['SECRET_KEY'] = \
        os.getenv("FLASK_SECRET_KEY", "secret-key-goes-here")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)



    @login_manager.user_loader
    def load_user(user_id):
        db_util = DbUtil()
        user = db_util.read(User).filter(User.id == user_id).first()
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return user

    # Register Blueprints
    app.register_blueprint(main.main)
    app.register_blueprint(auth.auth)

    return app


if __name__ == '__main__':
    create_app().run()