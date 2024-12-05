from flask import Blueprint, render_template, redirect, url_for, flash
from apps.app import db
from apps.auth.forms import LoginForm
from apps.crud.models import User
from apps.crud.forms import UserForm
from email_validator import validate_email, EmailNotValidError
from flask_login import login_user, logout_user     # session에 저장시켜줌

auth = Blueprint(
  "auth",
  __name__,
  template_folder="templates",
  static_folder="static"
)

@auth.route('/')
def index():
  return render_template('/auth/index.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  form = UserForm()
  
  if form.validate_on_submit():
    user = User(
      username = form.username.data,
      email = form.email.data,
      password = form.password.data
    )    
    # 회원가입 시 입력한 이메일이 DB에 있는지 검사
    # True : 중복 / False : 중복아님
    if user.is_duplicate_email():
      flash('중복 이메일')
      return redirect(url_for('auth.signup'))
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)     # 회원가입 처리되면 DB에 저장 후 로그인도 해줌
    return redirect(url_for('detector.index'))
    
  return render_template('auth/signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  
  if form.validate_on_submit():
    user = User.query.filter_by(username = form.username.data).first()
    
    if user is not None and user.verify_password(form.password.data): 
      login_user(user)
      return redirect(url_for('detector.index'))
    
    flash("아이디 또는 비밀번호가 틀립니다.") 

  return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('auth.login'))



