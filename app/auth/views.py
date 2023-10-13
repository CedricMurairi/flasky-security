from . import auth
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
import datetime


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and not user.is_verified:
            flash('Please check your inbox to confirm your email address')
            return redirect(url_for('auth.login'))

        if user and user.verify_password(password):
            login_user(user, remember=True,
                       duration=datetime.timedelta(days=365))
            flash('Login successful')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    return render_template('login.html')


@auth.route('/email/confirm/<token>')
def confirm_email(token):
    if token is None:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('index'))
    else:
        try:
            user_id = User.load_token(token)
            print(user_id)
        except:
            raise Exception('Invalid Token')

        user = User.query.filter_by(id=user_id).first()

        if user is None:
            flash('The confirmation link is invalid or has expired.')
            return redirect(url_for('index'))
        else:
            user.is_verified = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True,
                       duration=datetime.timedelta(days=365))
            flash('You have confirmed your account. Thanks!')
            return redirect(url_for('auth.change_password'))


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        password = request.form.get("password")
        user = User.query.filter_by(id=current_user.id).first()
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash('Password changed successfully')
        return redirect(url_for('index'))

    return render_template('change_password.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))
