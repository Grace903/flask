from datetime import datetime
from apps.app import db

class Board(db.Model):
  __tablename__ = 'board'
  id = db.Column(db.Integer, primary_key=True)   # primary_key=True : 기본키 컬럼
  subject = db.Column(db.String(255), nullable=False)
  content = db.Column(db.Text(), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
  # ondelete='CASCADE' : 부모 행 삭제 시 외래 키를 참조하는 자식 행도 함께 삭제
  
  # 양방향 참조 - 컬럼명 : user
  # 별도 join이나 select 없이 user로 board 정보, board로 user 정보 받을 수 있음
  # backref : 역참조 -> user에서 board 정보를 가져오기 위한 'boards' 생성
  user = db.relationship('User', backref = db.backref('boards'))

class Comment(db.Model):
  __tablename__ = 'comment'
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
  user = db.relationship('User', backref = db.backref('user_comments'))
  board_id = db.Column(db.Integer, db.ForeignKey('board.id', ondelete='CASCADE'), nullable=False)
  board = db.relationship('Board', backref = db.backref('comment_list'))
  
  
  