from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField
# FIleAllowed : 특정 확장자만 허용하게 하는 도구
# FileField : input 태그 넣기 위한~
# FileRequired : 유효성 검사

class UploadImageForm(FlaskForm):
  image = FileField(
    validators=[
      FileRequired('업로드할 이미지를 선택하세요'),
      FileAllowed(['jpg', 'jpeg', 'png'], "지원되지 않는 확장자입니다.")
    ]
  )
  submit = SubmitField()

class DeleteForm(FlaskForm):
  submit = SubmitField('삭제')  # 괄호 안에 버튼 이름 입력























