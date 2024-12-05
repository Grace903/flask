from flask import Flask, render_template, request, redirect, url_for, flash
from email_validator import validate_email, EmailNotValidError
import logging
from flask_debugtoolbar import DebugToolbarExtension
import os
from flask_mail import Mail, Message

app = Flask(__name__)

# 시크릿키 설정
app.config['SECRET_KEY'] = '1234'

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

# mail관련 설정 추가
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# 로그 레벨 설정
app.logger.setLevel(logging.DEBUG)

# 로그 출력
# app.logger.critical('치명적오류')
# app.logger.error('오류')
# app.logger.warning('경고')
# app.logger.info('info')
# app.logger.debug('debug')

@app.route('/')
def index():
  return 'Hello Flask'

@app.route('/hi/<name>')
def hi(name):
  return render_template('index.html', name=name)

@app.route('/contact')
def contact():
  return render_template('contact.html')

# get, post 뭐로 요청하든 다 contact_complete함수가 실행됨
@app.route('/contact/complete', methods=['GET', 'POST'])
def contact_complete():
  if request.method == 'POST':
    # POST요청 시 처리할 코드들
    username = request.form['username']
    email = request.form['email']
    description = request.form['description']

    is_vali = True

    if not username:
      flash('이름은 반드시 입력하세요')
      is_vali = False

    if not email:
      flash('이메일은 반드시 입력해야함')
      is_vali = False

    try:
      validate_email(email)
    except EmailNotValidError:
      flash('이메일 형식에 맞게 작성')
      is_vali = False

    if not description:
      flash('내용은 반드시 입력')
      is_vali = False

    if not is_vali:
      return redirect(url_for('contact'))


    send_mail(
      email, "문의 확인용 메일", "mail_form",
      username=username, description=description
    )
    # 위에 코드가 실행된 후 다시 contact_complete함수로 리다이렉트 함
    flash('빠르게 답변 드리겠습니다.')
    return redirect(url_for('contact_complete'))

  return render_template('contact_complete.html')

# 메일 전송처리 해주는 함수
def send_mail(to, subject, template, **kwargs):
  msg = Message(subject, recipients=[to])
  msg.body = render_template(template + '.txt', **kwargs)
  msg.html = render_template(template + '.html', **kwargs)
  mail.send(msg)