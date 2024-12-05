from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_login import LoginManager

from apps.config import config
import os

config_key = os.environ.get('FLASK_CONFIG_KEY')

# SQLAlchemy 객체 생성
db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '로그인 후 사용 가능합니다.'

def create_app():
  app = Flask(__name__)

  app.config.from_object(config[config_key])

  db.init_app(app)
  csrf.init_app(app)
  Migrate(app, db)
  login_manager.init_app(app)

  from apps.crud import views as crud_views
  from apps.auth import views as auth_views
  from apps.detector import views as dt_views
  from apps.board import views as board_views
  
  app.register_blueprint(crud_views.crud, url_prefix='/crud')
  app.register_blueprint(auth_views.auth, url_prefix='/auth')
  app.register_blueprint(dt_views.dt)
  app.register_blueprint(board_views.board, url_prefix='/board')
  app.register_blueprint(board_views.comment, url_prefix='/comment')
  
  app.register_error_handler(404, page_not_found)
  app.register_error_handler(500, internal_server_error)
  #  app.register_error_handler(Exception, internal_server_error) : 모든 에러 처리
  
  return app

def page_not_found(e):    # e 에는 에러메시지가 들어감
  return render_template('404.html'), 404

def internal_server_error(e):
  return render_template('500.html'), 500
  