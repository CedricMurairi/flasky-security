from . import auth
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
import datetime
from app.email import send_email


@auth.before_app_request
def before_request():
    if (current_user.is_authenticated and not current_user.is_verified and request.blueprint != 'auth' and request.endpoint != 'static'):
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_verified:
        return redirect('/')
    return render_template('account/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        # if user and not user.is_verified:
        #     flash('Please check your inbox to confirm your email address')
        #     return redirect(url_for('auth.login'))

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


@auth.route('/resend_confirmation/<int:id>')
def resend_confirmation(id):
    def send_verification_email(user):
        token = user.generate_confirmation_token()
        send_email(user.email, '[Again] Verify Your Account and Email',
                   'account/verify_email', user=user, token=token)

    user = User.query.get(id)
    if not user:
        flash('Something went wrong with your account. Try again later')
        return redirect(url_for('auth.login'))

    send_verification_email(user)
    flash('We have sent another confirmation email. Check your inbox.')
    return redirect(url_for('auth.unconfirmed'))


@auth.route('email/verify/<token>')
def verify_email(token):
    if token is None:
        flash('The verification linnk is invalid or has expired.')
        return redirect(url_for('index'))
    else:
        try:
            user_id = User.load_token(token)
        except:
            raise Exception('Invalid Token')

        user = User.query.get(user_id)

        if user is None:
            flash('The verification link is invalid or has expired.')
            return redirect(url_for('login'))
        else:
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


@auth.route('/request_password_change', methods=['GET', 'POST'])
def request_password_change():

    def send_verification_email(user):
        token = user.generate_confirmation_token()
        send_email(user.email, 'Reset Your Password',
                   'password/verify_email', user=user, token=token)

    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_verification_email(user)
            flash('A password reset link has been shared to your email')
            return redirect(url_for('auth.login'))

    return render_template('password/confirm_email.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))
