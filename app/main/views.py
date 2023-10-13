from . import main
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, Comment, Reply
from app import db


@main.route('/', methods=['GET'])
@login_required
def index():
    faculties = User.query.filter_by(is_faculty=True).all()
    return render_template('index.html', faculties=faculties)


@main.route('/comments', methods=['GET'])
@login_required
def comments():
    comments = Comment.query.filter_by(user_id=current_user.id).all()
    if current_user.is_faculty:
        fac_comments = Comment.query.filter_by(
            faculty_id=current_user.id).all()
    return render_template('comments.html', comments=comments, fac_comments=fac_comments if current_user.is_faculty else None)


@main.route('/comment', methods=['POST'])
@login_required
def comment():
    title = request.form.get("title")
    comment = request.form.get("comment")
    faculty_id = int(request.form.get("faculty"))

    comment = Comment(title=title, comment=comment,
                      faculty_id=faculty_id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully')
    return redirect(url_for('main.index'))


@main.route('/reply', methods=['POST'])
@login_required
def reply():
    comment_id = int(request.form.get("comment_id"))
    reply = request.form.get("reply")

    reply = Reply(comment_id=comment_id, reply=reply, user_id=current_user.id)
    db.session.add(reply)
    db.session.commit()
    flash('Reply added successfully')
    return redirect(url_for('main.comments'))


@main.route('/comment/<int:id>', methods=['GET'])
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully')
    return redirect(url_for('main.comments'))


@main.route('/reply/<int:id>', methods=['GET'])
@login_required
def delete_reply(id):
    reply = Reply.query.filter_by(id=id).first()
    db.session.delete(reply)
    db.session.commit()
    flash('Reply deleted successfully')
    return redirect(url_for('main.comments'))
