from flask import Blueprint, render_template, current_app, send_from_directory, redirect, url_for, flash, request
from flask_login import login_required, current_user
import uuid
from pathlib import Path
import random
import cv2
import torch
import torchvision
from PIL import Image
import numpy as np
import torchvision.transforms.functional
from flask_wtf.csrf import generate_csrf

from apps.detector.forms import UploadImageForm, DeleteForm
from apps.app import db
from apps.detector.models import UserImage, UserImageTag
from apps.crud.models import User

dt = Blueprint(
  "detector",
  __name__,
  template_folder="templates"
)

@dt.route('/')
def index():
  images = (
    db.session.query(User, UserImage)
              .join(UserImage)
              .filter(User.id == UserImage.user_id)
              .all()
  )

  csrf_token = generate_csrf()
  form = DeleteForm()

  user_image_tag_dict = {}

  for image in images:
    user_image_tags = (
      db.session.query(UserImageTag)
        .filter(UserImageTag.user_image_id == image.UserImage.id)
        .all()
    )
    user_image_tag_dict[image.UserImage.id] = user_image_tags

  return render_template('detector/index.html', images=images, user_image_tag_dict=user_image_tag_dict, csrf_token=csrf_token, form=form)

@dt.route('/images/<path:filename>')
def image_file(filename):
  return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@dt.route('/upload', methods=["GET", "POST"])
@login_required
def upload_image():
  form = UploadImageForm()

  if form.validate_on_submit():
    # 전송받은 파일을 저장
    file = form.image.data
    
    # 이미지 파일의 확장자 추출
    ext = Path(file.filename).suffix
    uuid_file_name = str( uuid.uuid4() ) + ext

    # 이미지를 저장
    image_path = Path(current_app.config['UPLOAD_FOLDER'], uuid_file_name)
    file.save(image_path)

    # DB에 저장
    user_image = UserImage(user_id=current_user.id, image_path=uuid_file_name)
    db.session.add(user_image)
    db.session.commit()
    
    # 저장이 끝나면 index페이지로 이동
    return redirect(url_for('detector.index'))

  return render_template('detector/upload.html', form=form)


# 랜덤 색상 리턴
def make_color(labels):
  colors = [[random.randint(0,255) for _ in range(3)] for _ in labels]
  color = random.choice(colors)
  return color

# 선 두께 생성
def make_line(result_image):
  line = round(max(result_image.shape[0:2]) * 0.002) + 1
  return line

# 이미지에 선을 그려주는 함수
def draw_lines(c1, c2, result_image, line, color):
  cv2.rectangle(result_image, c1, c2, color, thickness=line)
  return cv2


def draw_texts(result_image, line, c1, cv2, color, labels, label):
  display_text = f'{labels[label]}'
  font = max(line - 1, 1)
  t_size = cv2.getTextSize(display_text, 0, fontScale=line / 3, thickness=font)[0]
  c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
  cv2.rectangle(result_image, c1, c2, color, -1)
  cv2.putText(
    result_image, display_text, (c1[0], c1[1] - 2),
    0, line / 3, [255, 255, 255], thickness=font, lineType=cv2.LINE_AA
  )

  return cv2

def exec_detect(target_image_path):
  labels = current_app.config['LABELS']
  image = Image.open(target_image_path)

  image_tensor = torchvision.transforms.functional.to_tensor(image)
  model = torch.load(Path(current_app.root_path, 'detector', 'model.pt'))

  model = model.eval()

  output = model([image_tensor])[0]
  tags = []
  result_image = np.array(image.copy())

  for box, label, score in zip(output['boxes'], output['labels'], output['scores']):
    if score > 0.5 and labels[label] not in tags:
      color = make_color(labels)
      line = make_line(result_image)
      c1 = ( int(box[0]), int(box[1]) )
      c2 = ( int(box[2]), int(box[3]) )
      cv2 = draw_lines(c1, c2, result_image, line, color)
      cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
      tags.append(labels[label])

  if tags:
    detected_image = str(uuid.uuid4()) + '.jpg'

    detected_image_path = str( 
      Path(current_app.config['UPLOAD_FOLDER'], detected_image)
    )

    cv2.imwrite(detected_image_path, cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    return tags, detected_image
  else:
    return tags, None
  
def save_detected_image_tags(user_image, tags, detected_image):
  user_image.image_path = detected_image
  user_image.is_detected = True
  db.session.add(user_image)

  for tag in tags:
    user_image_tag = UserImageTag(user_image_id=user_image.id, tag_name=tag)
    db.session.add(user_image_tag)
  
  db.session.commit()

@dt.route('/detect/<string:image_id>', methods=["POST"])
@login_required
def detect(image_id):
  user_image = db.session.query(UserImage).filter(UserImage.id == image_id).first()

  if user_image is None:
    flash('해당 이미지가 존재하지 않습니다.')
    return redirect(url_for('detector.index'))

  target_image_path = Path(current_app.config['UPLOAD_FOLDER'], user_image.image_path)
  tags, detected_image = exec_detect(target_image_path)

  if not tags:
    flash('감지된 물체가 없습니다.')
    return redirect(url_for('detector.index'))
  
  try:
    save_detected_image_tags(user_image, tags, detected_image)
  except Exception as e:
    flash('물체 감지 결과 저장 중 오류가 발생')
    db.session.rollback()

  return redirect(url_for('detector.index'))

@dt.route('/images/delete/<string:image_id>', methods=['POST'])
@login_required
def delete_image(image_id): # 이미지 삭제 요청 위해 이미지 id 보냄
  try:
    db.session.query(UserImageTag).filter(UserImageTag.user_image_id == image_id).delete()
    db.session.query(UserImage).filter(UserImage.id == image_id).delete()
    db.session.commit()
  except Exception as e:
    flash('이미지 삭제 중 오류 발생')
    db.session.rollback()
    # SQLAlchemy에서 사용, 현재 트랜잭션을 롤백하여 세션 중에 이루어진 모든 변경 사항을 취소
    # 주로 데이터베이스에서 오류가 발생했을 때, 트랜잭션을 원래 상태로 되돌리기 위해 사용됩니다.
    
  return redirect(url_for('detector.index'))

@dt.route('/images/search')
def search():
  search_text = request.args.get('search')
  # URL의 쿼리 스트링에서 'search'라는 키의 값을 가져옵니다.
  # ?search=cat이라면 search_text는 'cat' / 검색어로 사용

  user_images = db.session.query(User, UserImage).join(UserImage, User.id == UserImage.user_id)
  # .join : User와 UserImage 테이블을 user_id를 기준으로 조인(join)하여, 각 사용자에 해당하는 이미지를 가져옵니다.
  
  user_image_tag_dict = {}    # 이미지와 태그의 관계를 저장할 딕셔너리
  filtered_user_images = []   # 검색 조건에 맞는 이미지를 저장할 빈 리스트
  
  # 일단 업로드 된 전체 이미지를 가져옴 : user_images
  # 전체 이미지를 하나씩 반복 돌림 -> 이미지마다 가지고 있는 태그를 꺼내서 검색어를 포함하는지 확인
  for user_image in user_images: 
    if not search_text:     # 검색어가 없으면 이미지에 해당하는 태그들을 가져옴 -> 모든 이미지에 해당하는 태그들이 가져와짐
      user_image_tags = (
        db.session.query(UserImageTag)
                  .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                  .all()
      )
    else:    
      user_image_tags = (      # 검색어가 있으면 이미지에 해당하는 태그들 중 검색어를 포함하는 것만 가져옴
        db.session.query(UserImageTag)
                  .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                  .filter(UserImageTag.tag_name.like('%' + search_text + '%'))
                  .all()
      )
      
      if not user_image_tags:   # 검색어에 해당하는 태그가 없으면 다음 이미지로 넘어감 (continue)
        continue
      
 # 검색어에 해당하는 태그가 있으면 결과화면에 검색어에 해당하는 태그 뿐만 아니라 전체 태그들을 다 보여주므로 다시 select 작업을 함
      user_image_tags = (   
        db.session.query(UserImageTag)
                  .filter(UserImageTag.user_image_id == user_image.UserImage.id)
                  .all()
      )
      # 최종 결과로 표시할 태그들을 저장하는 변수에 넣음
    user_image_tag_dict[user_image.UserImage.id] = user_image_tags    # 이미지id : 이미지id에 해당하는 태그 정보들
    filtered_user_images.append(user_image) # 검색어를 포함하는 이미지들을 저장해주는 배열
    
  form = DeleteForm()
  
  return render_template('detector/index.html', images = filtered_user_images, user_image_tag_dict=user_image_tag_dict, form=form)