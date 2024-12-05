from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import length, DataRequired, Email

class UserForm(FlaskForm):
  username = StringField(
    "사용자명",
    validators=[
      DataRequired(message='사용자명은 필수입니다.'),
      length(max=30, message='30자 이하로 입력하세요')
    ]
  )

  email = StringField(
    "메일주소",
    validators=[
      DataRequired(message='이메일은 필수로 입력'),
      Email(message='메일 주소 형식으로 입력')
    ]
  )

  password = PasswordField(
    "비밀번호",
    validators=[
      DataRequired(message='비밀번호는 반드시 입력')
    ]
  )

  submit = SubmitField("회원가입")