from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
  # FlaskForm을 상속받는 LoginForm 클래스 생성
  username = StringField(
    "아이디",
    validators=[
      DataRequired('아이디는 필수 입력'),
      Length(max=30, message = '30자 이하만 입력 가능')
    ]
  )
  password = PasswordField(
    "비밀번호",
    validators=[
      DataRequired('비밀번호 필수 입력')
    ]
  )
  submit = SubmitField('로그인')