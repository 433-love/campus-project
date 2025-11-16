from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class UserRole(enum.Enum):
    User = "User"
    Admin = "Admin"


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nickname = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.User)


class Cat(Base):
    __tablename__ = "cats"
    cat_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    health_status = Column(String, nullable=True)
    sightings = relationship("SightingLog", back_populates="cat", cascade="all, delete-orphan")
    feedings = relationship("FeedingLog", back_populates="cat", cascade="all, delete-orphan")


class SightingLog(Base):
    __tablename__ = "sighting_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cat_id = Column(Integer, ForeignKey("cats.cat_id"), nullable=False)
    photo_url = Column(String, nullable=True)
    location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    cat = relationship("Cat", back_populates="sightings")


class FeedingLog(Base):
    __tablename__ = "feeding_logs"
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    cat_id = Column(Integer, ForeignKey("cats.cat_id"), nullable=False)
    food_type = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    cat = relationship("Cat", back_populates="feedings")


class CommunityPost(Base):
    __tablename__ = "community_posts"
    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content_text = Column(Text, nullable=False)
    content_image_url = Column(String, nullable=True)
    ai_generated_text = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    likes_count = Column(Integer, default=0, nullable=False)
    comments_count = Column(Integer, default=0, nullable=False)


class CommunityPostLike(Base):
    __tablename__ = "community_post_likes"
    like_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.post_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = ({},)


class CommunityPostComment(Base):
    __tablename__ = "community_post_comments"
    comment_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.post_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)


class Badge(Base):
    __tablename__ = "badges"
    badge_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)


class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.badge_id"), nullable=False)
    acquisition_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    __table_args__ = ({},)