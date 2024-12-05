
document.querySelector('.comment-list').addEventListener('click', (e) => {
  const commentId = e.target.dataset.commentId
  
  if (e.target.classList.contains(`edit-comment-btn`)) {
    // 댓글 내용이 작성되어있는 p태그
    const contentText = document.querySelector(`#content-text-${commentId}`);
    // 댓글을 수정할 수 있는 textarea
    const contentEdit = document.querySelector(`#content-edit-${commentId}`);
    // 수정버튼
    const editButton = e.target;
    // 저장버튼
    const saveButton = document.querySelector(`#comment-${commentId} .save-comment-btn`);

    contentText.classList.add(`d-none`);
    editButton.classList.add(`d-none`);
    contentEdit.classList.remove(`d-none`);
    saveButton.classList.remove(`d-none`);
  }

  if (e.target.classList.contains('save-comment-btn')) {
    const csrfToken = document.querySelector(`input[name="csrf_token"]`).value;
    const newContent = document.querySelector(`#content-edit-${commentId}`).value;

    fetch(`/comment/${commentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify({ 'content': newContent })
    }).then(response => response.json())
      .then(data => {
        if (data.status == 'success') {
          alert(data.message);

          document.querySelector(`#content-text-${commentId}`).innerText = newContent;
          document.querySelector(`#content-text-${commentId}`).classList.remove(`d-none`);
          document.querySelector(`#comment-${commentId}.edit-comment-btn`).classList.remove(`d-none`);
          document.querySelector(`#content-edit-${commentId}`).classList.add(`d-none`);
          e.target.classList.add(`d-none`);
        } else {
          alert('댓글 수정 실패')
        }
      })
  }
})




document.querySelector('.delete-board').addEventListener('click', (e) => {
  e.preventDefault()

  if (confirm('정말로 삭제하시겠습니까?')) {
    location.href = e.target.href
  }
})



const deleteComment = async (commentId) => {
  const csrfToken = document.querySelector('input[name="csrf_token"]').value

  const response = await fetch(`/comment/${commentId}`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': csrfToken
    }
  })

  const data = await response.json();
  console.log(data)
}

