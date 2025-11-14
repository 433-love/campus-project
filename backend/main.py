from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
import shutil

from .database import Base, engine, SessionLocal
from .models import Cat, SightingLog, FeedingLog, User, Badge, UserBadge, CommunityPost
from .schemas import CatCreate, CatUpdate, CatSummary, SightingCreate, FeedingCreate, TimelineItem
from .utils import get_request_user


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
except Exception:
    pass


@app.post("/api/admin/cats", response_model=CatSummary)
def create_cat(payload: CatCreate, db: Session = Depends(get_db), req_user=Depends(get_request_user)):
    if req_user["role"] != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    cat = Cat(
        name=payload.name,
        profile_image_url=payload.profile_image_url,
        description=payload.description,
        health_status=payload.health_status,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@app.put("/api/admin/cats/{cat_id}", response_model=CatSummary)
def update_cat(cat_id: int, payload: CatUpdate, db: Session = Depends(get_db), req_user=Depends(get_request_user)):
    if req_user["role"] != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


@app.delete("/api/admin/cats/{cat_id}")
def delete_cat(cat_id: int, db: Session = Depends(get_db), req_user=Depends(get_request_user)):
    if req_user["role"] != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found")
    db.delete(cat)
    db.commit()
    return {"deleted": True}


@app.get("/api/cats", response_model=List[CatSummary])
def list_cats(db: Session = Depends(get_db)):
    cats = db.query(Cat).all()
    return [CatSummary(cat_id=c.cat_id, name=c.name, profile_image_url=c.profile_image_url) for c in cats]


@app.post("/api/sightings")
async def create_sighting(
    user_id: int | None = Form(default=None),
    cat_id: int = Form(...),
    location: str = Form(...),
    photo_url: str | None = Form(default=None),
    photo: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    req_user=Depends(get_request_user),
):
    uid = user_id or req_user.get("user_id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id required")
    stored_url = photo_url
    if photo is not None:
        os.makedirs("uploads", exist_ok=True)
        filename = f"{cat_id}_{uid}_{photo.filename}"
        filepath = os.path.join("uploads", filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(photo.file, f)
        stored_url = f"/uploads/{filename}"
    if not stored_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="photo or photo_url required")
    sight = SightingLog(user_id=uid, cat_id=cat_id, photo_url=stored_url, location=location)
    db.add(sight)
    db.commit()
    db.refresh(sight)
    ensure_badges_after_sighting(db, uid)
    return {"log_id": sight.log_id}


@app.post("/api/feedings")
def create_feeding(payload: FeedingCreate, db: Session = Depends(get_db), req_user=Depends(get_request_user)):
    uid = payload.user_id or req_user.get("user_id")
    if not uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id required")
    feed = FeedingLog(user_id=uid, cat_id=payload.cat_id, food_type=payload.food_type, amount=payload.amount)
    db.add(feed)
    db.commit()
    db.refresh(feed)
    ensure_badges_after_feeding(db, uid)
    return {"log_id": feed.log_id}


@app.get("/api/cats/{cat_id}/timeline", response_model=List[TimelineItem])
def cat_timeline(cat_id: int, db: Session = Depends(get_db)):
    cat = db.get(Cat, cat_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found")
    sightings = [
        TimelineItem(
            type="sighting",
            timestamp=s.timestamp,
            data={"log_id": s.log_id, "photo_url": s.photo_url, "location": s.location, "user_id": s.user_id},
        )
        for s in db.query(SightingLog).filter(SightingLog.cat_id == cat_id).all()
    ]
    feedings = [
        TimelineItem(
            type="feeding",
            timestamp=f.timestamp,
            data={"log_id": f.log_id, "food_type": f.food_type, "amount": f.amount, "user_id": f.user_id},
        )
        for f in db.query(FeedingLog).filter(FeedingLog.cat_id == cat_id).all()
    ]
    items = sightings + feedings
    items.sort(key=lambda x: x.timestamp, reverse=True)
    return items


def get_or_create_badge(db: Session, name: str, description: str, icon_url: str | None = None) -> Badge:
    badge = db.query(Badge).filter(Badge.name == name).first()
    if badge:
        return badge
    badge = Badge(name=name, description=description, icon_url=icon_url)
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


def award_badge_if_not_exists(db: Session, user_id: int, badge_name: str, description: str):
    badge = get_or_create_badge(db, badge_name, description)
    exists = db.query(UserBadge).filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge.badge_id).first()
    if exists:
        return
    ub = UserBadge(user_id=user_id, badge_id=badge.badge_id)
    db.add(ub)
    db.commit()


def ensure_badges_after_sighting(db: Session, user_id: int):
    total = db.query(SightingLog).filter(SightingLog.user_id == user_id).count()
    if total == 1:
        award_badge_if_not_exists(db, user_id, "爱心初体验", "首次成功上报轨迹")
    distinct_locations = db.query(SightingLog.location).filter(SightingLog.user_id == user_id).distinct().count()
    if distinct_locations >= 5:
        award_badge_if_not_exists(db, user_id, "校园探险家", "上报地点达到 5 种")
    distinct_cats = db.query(SightingLog.cat_id).filter(SightingLog.user_id == user_id).distinct().count()
    if distinct_cats >= 10:
        award_badge_if_not_exists(db, user_id, "全图鉴", "上报猫咪达到 10 种")


def ensure_badges_after_feeding(db: Session, user_id: int):
    total = db.query(FeedingLog).filter(FeedingLog.user_id == user_id).count()
    if total == 1:
        award_badge_if_not_exists(db, user_id, "首次投喂", "首次投喂猫咪")
    if total >= 50:
        award_badge_if_not_exists(db, user_id, "头号铲屎官", "投喂次数达到 50 次")


@app.get("/api/users/{user_id}/profile")
def user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        return {"nickname": "校园爱猫人", "avatar_url": None}
    return {"nickname": user.nickname, "avatar_url": user.avatar_url}


@app.get("/api/users/{user_id}/badges")
def user_badges(user_id: int, db: Session = Depends(get_db)):
    rows = (
        db.query(UserBadge, Badge)
        .join(Badge, Badge.badge_id == UserBadge.badge_id)
        .filter(UserBadge.user_id == user_id)
        .all()
    )
    return [
        {"badge_id": b.badge_id, "name": b.name, "description": b.description, "icon_url": b.icon_url}
        for (_, b) in rows
    ]


@app.post("/api/community/posts")
def create_post(user_id: int = Form(...), content_text: str = Form(...), content_image: UploadFile | None = File(default=None), db: Session = Depends(get_db)):
    image_url = None
    if content_image is not None:
        os.makedirs("uploads", exist_ok=True)
        filename = f"post_{user_id}_{content_image.filename}"
        filepath = os.path.join("uploads", filename)
        with open(filepath, "wb") as f:
            shutil.copyfileobj(content_image.file, f)
        image_url = f"/uploads/{filename}"
    post = CommunityPost(user_id=user_id, content_text=content_text, content_image_url=image_url)
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"post_id": post.post_id}


@app.get("/api/community/posts")
def list_posts(page: int = 1, size: int = 20, db: Session = Depends(get_db)):
    q = db.query(CommunityPost).order_by(CommunityPost.timestamp.desc())
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return {
        "page": page,
        "size": size,
        "total": total,
        "items": [
            {
                "post_id": p.post_id,
                "user_id": p.user_id,
                "content_text": p.content_text,
                "content_image_url": p.content_image_url,
                "ai_generated_text": p.ai_generated_text,
                "timestamp": p.timestamp.isoformat(),
            }
            for p in items
        ],
    }


def get_llm_prompt(user_input_text: str) -> str:
    system_prompt = (
        "你是一个“猫咪翻译官”，你的任务是把用户描述的关于猫咪的事件，用“猫咪的第一人称口吻”（比如自称本喵、朕）来补充一句评论。\n"
        "风格要求：\n1. 必须可爱、傲娇或慵懒。\n2. 必须使用 Emoji (例如 🐱, 🐾, 💤, 🐟)。\n3. 必须简短，控制在 50 字以内。"
    )
    full_prompt = f"{system_prompt}\n---\n[用户输入]\n{user_input_text}\n---\n[你的输出]"
    return full_prompt


@app.post("/api/ai/generate-cat-speech")
def generate_cat_speech(user_text: str = Form(...)):
    prompt = get_llm_prompt(user_text)
    fallback = "本喵表示：太阳暖暖，先睡一觉再说~ 🐱💤"
    return {"text": fallback, "prompt": prompt}