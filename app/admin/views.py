from . import admin
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Comment, Reply
from app import db
from functools import wraps
from app.email import send_email


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if not current_user.is_admin:
            return render_template('401.html'), 401

        return func(*args, **kwargs)

    return decorated_view


@admin.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@admin.route('/add_user', methods=['POST'])
@login_required
@admin_required
def add_user():

    def send_verification_email(user, password):
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'verify_email', user=user, password=password, token=token)

    name = request.form.get("name")
    email = request.form.get("email")
    is_admin = True if request.form.get("role") == 'is_admin' else False
    is_faculty = True if request.form.get("role") == 'is_faculty' else False
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('admin.users'))

    user = User(name=name, email=email,
                is_admin=is_admin, is_faculty=is_faculty)
    user.password = password
    db.session.add(user)
    db.session.commit()

    send_verification_email(user, password)
    flash('User added successfully')
    return redirect(url_for('admin.users'))


@admin.route('/delete_user/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('admin.users'))


@admin.route('/comments', methods=['GET', 'POST'])
@login_required
@admin_required
def comments():
    faculties = User.query.filter_by(is_faculty=True).all()
    all_comments = Comment.query.all()
    return render_template('comments.html', faculties=faculties, all_comments=all_comments)


@admin.route('/reply', methods=['POST'])
@login_required
@admin_required
def reply():
    comment_id = int(request.form.get("comment_id"))
    reply = request.form.get("reply")

    reply = Reply(comment_id=comment_id, reply=reply, user_id=current_user.id)
    db.session.add(reply)
    db.session.commit()
    flash('Reply added successfully')
    return redirect(url_for('admin.comments'))


@admin.route('/comment/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully')
    return redirect(url_for('admin.comments'))


@admin.route('/reply/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_reply(id):
    reply = Reply.query.filter_by(id=id).first()
    db.session.delete(reply)
    db.session.commit()
    flash('Reply deleted successfully')
    return redirect(url_for('admin.comments'))
