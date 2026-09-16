import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from redis_client import redis_client
import models, schemas, auth

router = APIRouter(prefix="/posts", tags=["Posts"])


# 1. جلب كافة المقالات مع التخزين المؤقت (Caching + Pagination)
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # مفتاح التخزين يحتوي على قيم skip و limit لتمييز الصفحات
    cache_key = f"posts:skip_{skip}:limit_{limit}"

    # أ) فحص البيانات المخبأة في Redis
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    # ب) الاستعلام من قاعدة البيانات عند عدم وجود Cache
    posts = db.query(models.Post).offset(skip).limit(limit).all()

    # تحويل الكائنات إلى القاموس (Dict) ليتم تخزينها بصيغة JSON
    posts_data = [schemas.PostResponse.model_validate(p).model_dump() for p in posts]

    # ج) حفظ البيانات في Redis لمدة 60 ثانية
    redis_client.setex(cache_key, 60, json.dumps(posts_data, default=str))

    return posts


# 2. جلب مقال واحد برقمه (Single Post Caching)
@router.get("/{post_id}", response_model=schemas.PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    cache_key = f"post:{post_id}"

    cached_post = redis_client.get(cache_key)
    if cached_post:
        return json.loads(cached_post)

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    post_data = schemas.PostResponse.model_validate(post).model_dump()
    redis_client.setex(cache_key, 60, json.dumps(post_data, default=str))

    return post


# 3. إنشاء مقال جديد وتفريغ الـ Cache
@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    new_post = models.Post(**post.model_dump(), user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # حذف كافة المفاتيح المخبأة للمقالات لضمان تحديث القائمة
    for key in redis_client.scan_iter("posts:*"):
        redis_client.delete(key)

    return new_post


# 4. تعديل مقال وتحديث الـ Cache
@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int, 
    updated_post: schemas.PostUpdate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    post = post_query.first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    update_data = updated_post.model_dump(exclude_unset=True)
    post_query.update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(post)

    # مسح كاش المقال المحدد وكاش القوائم
    redis_client.delete(f"post:{post_id}")
    for key in redis_client.scan_iter("posts:*"):
        redis_client.delete(key)

    return post


# 5. حذف مقال ومسحه من الـ Cache
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(auth.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    db.delete(post)
    db.commit()

    # مسح كاش المقال المحذوف وكاش القوائم
    redis_client.delete(f"post:{post_id}")
    for key in redis_client.scan_iter("posts:*"):
        redis_client.delete(key)

    return