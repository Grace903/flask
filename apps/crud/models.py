from datetime import datetime

from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
  # 테이블명 설정
  __tablename__ = 'users'
  # 컬럼 설정
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), index=True)
  email = db.Column(db.String(255), unique=True, index=True)
  password_hash = db.Column(db.String(255))
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

  @property
  def password(self):
    raise AttributeError('비밀번호는 접근이 불가능 합니다.')

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)

  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  def is_duplicate_email(self):
    return User.query.filter_by(email = self.email).first() is not None
  
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)