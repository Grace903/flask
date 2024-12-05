from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user

from apps.app import db
from apps.crud.models import User
from apps.board.models import Board, Comment
from apps.board.forms import BoardForm, DeleteForm, CommentForm

board = Blueprint( 
  'board',
  __name__,
  template_folder='templates/board',
  static_folder='static'
)

comment = Blueprint(
  'comment',
  __name__,
  template_folder='templates/board',
  static_folder='static'
)

# 임시 게시글 300개 추가 / url에 dummy 입력하면 자동 생성됨
# @board.route('/dummy')
# def make_dummy():
#   for i in range(300):
#     board=Board(
#     subject = f'임시제목{i}',
#     content = f'임시내용{i}',
#     user_id = 1
#     )
#     db.session.add(board)
#     db.session.commit()    

@board.route('/')
def index(): 
  #몇 페이지를 보려고 하는지 저장
  page = request.args.get('page', type=int, default=1)    # 페이지 번호
  boards = Board.query.order_by(Board.created_at.desc()).paginate(page=page, per_page=10)
  

  
  print('------------------------------')
  print('현재 페이지의 레코드', boards.items)
  print('전체 수', boards.total)
  print('페이지 당 표시할 레코드 수', boards.per_page)
  print('현재 페이지 번호', boards.page)
  print('페이지 범위', boards.iter_pages)
  print('이전 페이지 번호', boards.prev_num)
  print('다음 페이지 번호', boards.next_num)
  print('이전 페이지 있나?', boards.has_prev)
  print('다음 페이지 있나?', boards.has_next)
  print('------------------------------')
   
  return render_template('index.html', boards=boards)

@board.route('/new', methods=['GET', 'POST'])
@login_required
def new_board():
  form = BoardForm()
  
  if form.validate_on_submit():
    board = Board(
        user_id=current_user.id,
        subject=form.subject.data,
        content=form.content.data
    )
    db.session.add(board)
    db.session.commit()
    
    return redirect(url_for('board.index'))
    
  return render_template('new.html', form=form)

@board.route('/detail/<int:board_id>', methods=['GET', 'POST'])
@login_required
def detail_board(board_id):
  board = Board.query.get_or_404(board_id)
  form = CommentForm()

  if form.validate_on_submit():
    new_comment = Comment(
        user_id=current_user.id,
        content=form.content.data,
        board_id=board.id
    )
    db.session.add(new_comment)
    db.session.commit()
    
    return redirect(url_for('board.detail_board', board_id=board.id, comment=comment))

  return render_template('detail.html', board=board, form=form)  # jinja로 보내줌

@board.route('/update/<int:board_id>', methods=['GET','POST'])
def board_edit(board_id):
  board = Board.query.get_or_404(board_id)
  form = BoardForm(obj = board)
  
  if form.validate_on_submit():
    board.subject = form.subject.data
    board.content = form.content.data
      
    db.session.add(board)
    db.session.commit()
  
    return redirect(url_for('board.detail_board', board_id=board_id))
  
  return render_template ('edit.html', board=board, form=form)

# @board.route('/update', methods=['POST'])
# @login_required
# def update_board():
#   form = BoardForm()

#   return render_template('update.html', form=form)

@board.route('/delete/<int:board_id>', methods=['GET','POST'])
@login_required
def delete_board(board_id):
  board = Board.query.get(board_id)
  db.session.delete(board)
  db.session.commit()
    
  return redirect(url_for('board.index'))
    
@comment.route('/new/<board_id>', methods=['POST'])
@login_required
def new_comment(board_id):
  content = request.form['content']
  comment = Comment(content=content, user_id=current_user.id, board_id=board.id)

  db.session.add(comment)
  db.session.commit()
    
  return redirect(url_for('board.detail_board', board_id=board.id))

@comment.route('/detail/<int:board_id>')
def comment_list():
  comments = Comment.query.filter_by(board_id=board.id).order_by(Comment.created_at.desc()).all()
  form = CommentForm()
  
  if form.validate_on_submit():
    new_comment = Comment(content=form.content.data, board_id=board.id, user_id=current_user.id)
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('comment.comment_list', board_id=board.id))
 
  return render_template('detail.html', form=form, board=board, comments=comments)

@comment.route('/<comment_id>', methods=['PUT'])
@login_required
def edit_comment(comment_id):
  data = request.json # client가 요청하면 body에 담간 data 받아옴 ->수정할 댓글 내용
  comment = Comment.query.get(comment_id) # db에 수정할 댓글 id에 해당되는 레코드 추출 
 
  comment.content = data.get('content')
  
  try:
    db.session.commit()
    return jsonify({
      'message': '댓글 수정 완료',
      'content': comment.content,
      'status':'success'
    }), 200
  except Exception as e:
    db.session.rollback()
    return jsonify({'message' : '댓글 수정 실패', 'status' : 'error'}), 500
  
  # board = Board.query.get_or_404(comment.board_id)  # comment의 board_id를 이용하여 Board 객체를 조회
  # form = CommentForm(obj=comment)

  # if form.validate_on_submit():
  #   comment.content = form.content.data

  #   return redirect(url_for('board.detail_board', board_id=board.id))

  # return render_template('detail.html', form=form, board=board, comment=comment)

# detail.html에서 jinja로 comment_id 보내면 views.py의 route도 comment_id로 받아야 함
@comment.route('/<comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
  comment = Comment.query.get_or_404(comment_id)

  try:
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message' : '댓글 삭제 완료'}), 200
  except Exception as e:
    db.session.rollback()
   
    return jsonify({'message' : '댓글 삭제 실패'}), 500