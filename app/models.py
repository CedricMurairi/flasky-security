from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin
from app import db, login_manager
from itsdangerous import URLSafeTimedSerializer as Serializer
import os
from dotenv import load_dotenv

load_dotenv()

serializer = Serializer(os.getenv("SECRET_KEY") or os.urandom(
    32), salt='Email Confirmation')


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(120), unique=True)
    password_hash = Column(String(256))
    is_admin = Column(Boolean, default=False)
    is_faculty = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    def __init__(self, name=None, email=None, is_admin=False, is_faculty=False, is_verified=False):
        self.name = name
        self.email = email
        self.is_admin = is_admin
        self.is_faculty = is_faculty
        self.is_verified = is_verified

    def __repr__(self):
        return '<User %r>' % (self.email)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_faculty": self.is_faculty,
            "is_verified": self.is_verified
        }

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self):
        return serializer.dumps({'confirm': self.id})

    @staticmethod
    def load_token(token):
        data = serializer.loads(token)
        return data.get('confirm', None)


class Comment(UserMixin, db.Model):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    title = Column(String(120))
    comment = Column(String(120))
    timestamp = Column(db.DateTime)
    faculty_id = Column(Integer, ForeignKey('users.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", foreign_keys=[
                        user_id], backref="comments", cascade="all, delete")
    faculty = relationship("User", foreign_keys=[
                           faculty_id], backref="received_comments")

    def __init__(self, title, comment=None, faculty_id=None, user_id=None):
        self.title = title
        self.comment = comment
        self.faculty_id = faculty_id
        self.user_id = user_id

    def __repr__(self):
        return '<Comment %r>' % (self.comment)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "comment": self.comment,
            "faculty_id": self.faculty_id,
            "user_id": self.user_id,
            "user": self.user.to_dict(),
            "faculty": self.faculty.to_dict()
        }


class Reply(UserMixin, db.Model):
    __tablename__ = 'replies'
    id = Column(Integer, primary_key=True)
    reply = Column(String(120))
    timestamp = Column(db.DateTime)
    comment_id = Column(Integer, ForeignKey('comments.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", foreign_keys=[
                        user_id], backref="replies", cascade="all, delete")
    comment = relationship("Comment", foreign_keys=[
                           comment_id], backref="replies", cascade="all, delete")

    def __init__(self, reply=None, comment_id=None, user_id=None):
        self.reply = reply
        self.comment_id = comment_id
        self.user_id = user_id

    def __repr__(self):
        return '<Reply %r>' % (self.reply)

    def to_dict(self):
        return {
            "id": self.id,
            "reply": self.reply,
            "comment_id": self.comment_id,
            "user_id": self.user_id,
            "user": self.user.to_dict(),
            "comment": self.comment.to_dict()
        }
