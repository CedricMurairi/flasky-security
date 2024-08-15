from app.models import User
from app import create_app, db
import click
from flask.cli import with_appcontext
import os
from dotenv import load_dotenv
from app.models import User

load_dotenv()

app = create_app()


@click.command()
@with_appcontext
def initdb():
    db.create_all()

    # Add admin user if it doesn't exist
    if not User.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first():
        admin = User(name=os.getenv("ADMIN_NAME"), email=os.getenv(
            "ADMIN_EMAIL"), is_admin=True, is_verified=True)
        admin.password = os.getenv("ADMIN_PASSWORD")
        db.session.add(admin)
        db.session.commit()

    click.echo('Initialized the database.')


app.cli.add_command(initdb)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
