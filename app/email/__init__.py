from flask import render_template
from flask_mail import Message
from app import mail

import os

def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.sender = (os.getenv("ADMIN_NAME"), os.getenv("ADMIN_EMAIL"))
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
