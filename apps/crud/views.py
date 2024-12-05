from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from apps.crud.forms import UserForm
from apps.crud.models import User
from apps.app import db

crud = Blueprint(
  "crud",
  __name__,
  template_folder="templates",
  static_folder="static"
)

@crud.route('/')
def index():
  return render_template('crud/index.html')

@crud.route('/users/new', methods=["GET", "POST"])
@login_required
def create_user():
  form = UserForm()

  if form.validate_on_submit():
    # db에 저장할 객체 설정
    user = User(
      username = form.username.data,
      email = form.email.data,
      password = form.password.data
    )
    # db에 insert 시키고
    db.session.add(user)
    db.session.commit()

    # 회원가입 완료 페이지 이동
    return redirect(url_for('crud.users'))
  
  return render_template('crud/create.html', form=form)

@crud.route('/users')
@login_required
def users():
  # 회원정보들을 db에서 가져오는 코드
  users = User.query.all()

  return render_template('crud/index.html', users=users)

@crud.route('/users/<user_id>', methods=['GET', 'POST'])
@login_required
def user_edit(user_id):
    form = UserForm()
    user = User.query.filter_by(id=user_id).first()
    
    if form.validate_on_submit():
      user.username = form.username.data
      user.email = form.email.data
      user.password = form.password.data      
      
      db.session.add(user)
      db.session.commit()
      
      return redirect(url_for('crud.users'))

    return render_template('crud/edit.html', user=user, form=form)


@crud.route('/users/<user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
  # User = User.query.filter_by(id = user_id).delete()
  # db.session.commit()
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()

    return redirect(url_for('crud.users'))