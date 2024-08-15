from flask import Flask, render_template
from flask_login import LoginManager
from config import config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData
from flask_mail import Mail
from flask_migrate import Migrate
import os

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


class Base(DeclarativeBase):
    pass


metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

db = SQLAlchemy(model_class=Base, metadata=metadata)
mail = Mail()
migrate = Migrate()


def create_app():
    config_name = os.getenv('FLASK_ENV') or 'default'

    app = Flask(__name__, static_folder="static")
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)

    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from .auth import auth as auth_blueprint
    from .main import main as main_blueprint
    from .admin import admin as admin_blueprint

    app.register_blueprint(main_blueprint, url_prefix='/')
    app.add_url_rule('/', endpoint='index')
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    @app.route('/hello')
    def hello():
        return '<h2>Hello world.</h2>'

    @app.errorhandler(500)
    def handle_500(e):
        return render_template('500.html'), 500

    @app.errorhandler(404)
    def handle_404(e):
        return render_template('404.html'), 404

    return app
