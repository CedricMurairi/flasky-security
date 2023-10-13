from app.models import User, Comment
from app import create_app, db, migrate
import os
from dotenv import load_dotenv
from app.models import User, Comment, Reply

load_dotenv()

app = create_app(os.getenv('FLASK_ENV') or 'default')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    with app.app_context():
        # Create database tables for our data models
        db.create_all()
        # Add admin user if it doesn't exist
        if not User.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first():
            admin = User(name=os.getenv("ADMIN_NAME"), email=os.getenv(
                "ADMIN_EMAIL"), is_admin=True, is_verified=True)
            admin.password = os.getenv("ADMIN_PASSWORD")
            db.session.add(admin)
            db.session.commit()
