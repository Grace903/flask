from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired

class BoardForm(FlaskForm):
  subject = StringField(
    "제목",
    validators=[DataRequired('제목을 입력하세요.')]
  )
  
  content = TextAreaField(
    "내용",
    validators=[DataRequired('내용을 입력하세요.')],
    render_kw={'rows': 10} 
    )
  
  submit = SubmitField('등록')

class DeleteForm(FlaskForm):
  submit = SubmitField('삭제')
  
class CommentForm(FlaskForm):
  content  = TextAreaField(
    "댓글",
    validators=[DataRequired('댓글을 입력하세요.')]
    )
  submit = SubmitField('등록')