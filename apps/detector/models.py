from datetime import datetime
from apps.app import db   # db : app.py 파일의 SQLAlchemy / init, migrate 다 들어있음

class UserImage(db.Model):
  __tablename__ = 'user_image'
  id = db.Column(db.Integer, primary_key=True)  # primary_key=True : 기본키 컬럼
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  image_path = db.Column(db.String(255))
  is_detected = db.Column(db.Boolean, default = False)
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class UserImageTag(db.Model):
  __tablename__='user_image_tags'
  id = db.Column(db.Integer, primary_key=True)
  user_image_id = db.Column(db.Integer, db.ForeignKey('user_image.id'))
  tag_name = db.Column(db.String(255))
  created_at = db.Column(db.DateTime, default=datetime.now)
  updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)