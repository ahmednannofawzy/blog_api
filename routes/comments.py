from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/{post_id}", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(post_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = models.Comment(text=comment.text, post_id=post_id, user_id=current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    comment_query = db.query(models.Comment).filter(models.Comment.id == comment_id)
    comment = comment_query.first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    comment_query.delete(synchronize_session=False)
    db.commit()
    return