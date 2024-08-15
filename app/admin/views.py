from . import admin
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Item
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


def manager_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        if not (current_user.is_manager or current_user.is_admin):
            return render_template('401.html'), 401

        return func(*args, **kwargs)

    return decorated_view


@admin.route('/users', methods=['GET'])
@login_required
@manager_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)


@admin.route('/add_user', methods=['POST'])
@login_required
@manager_required
def add_user():

    def send_verification_email(user):
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'account/verify_email', user=user, token=token)

    name = request.form.get("name")
    email = request.form.get("email")
    user_type = request.form.get("user_type")
    is_admin = False
    is_manager = False
    is_supplier = False
    if user_type == "admin":
        is_admin = True
    elif user_type == "manager":
        is_manager = True
    else:
        is_supplier = True
    password = request.form.get("password")

    if User.query.filter_by(email=email).first():
        flash('Email already exists')
        return redirect(url_for('admin.users'))

    user = User(name=name, email=email,
                is_admin=is_admin, is_manager=is_manager, is_supplier=is_supplier)
    user.password = password
    db.session.add(user)
    db.session.commit()

    send_verification_email(user)
    flash('User added successfully')
    return redirect(url_for('admin.users'))


@admin.route('/delete_item/<int:id>', methods=['GET'])
@login_required
@admin_required
def delete_item(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully')
    return redirect(url_for('admin.items'))


@admin.route('/items', methods=['GET'])
@login_required
@admin_required
def items():
    items = Item.query.all()
    return render_template('items.html', items=items)


@admin.route('/add_item', methods=['POST'])
@login_required
@admin_required
def add_item():
    name = request.form.get("name")
    description = request.form.get("description")

    item = Item(name=name, description=description)
    db.session.add(item)
    db.session.commit()
    flash('Item added successfully')
    return redirect(url_for('admin.items'))


@admin.route('/delete_user/<int:id>', methods=['GET'])
@login_required
@manager_required
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('admin.users'))
