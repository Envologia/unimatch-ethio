from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum,
    Table,
    UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

class Gender(enum.Enum):
    """Gender options for users."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class University(enum.Enum):
    AAU = "Addis Ababa University"
    ASTU = "Adama Science and Technology University"
    BDU = "Bahir Dar University"
    JU = "Jimma University"
    HU = "Hawassa University"
    MU = "Mekelle University"
    WU = "Wollega University"
    DU = "Dire Dawa University"
    AMU = "Arba Minch University"
    SU = "Semera University"

class MatchStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNMATCHED = "unmatched"

class ConfessionStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ReportStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(32), unique=True)
    first_name = Column(String(64))
    last_name = Column(String(64))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    sent_matches = relationship("Match", foreign_keys="Match.sender_id", back_populates="sender")
    received_matches = relationship("Match", foreign_keys="Match.receiver_id", back_populates="receiver")
    confessions = relationship("Confession", back_populates="user")
    sent_reports = relationship("Report", foreign_keys="Report.reporter_id", back_populates="reporter")
    received_reports = relationship("Report", foreign_keys="Report.reported_id", back_populates="reported")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    university = Column(Enum(University), nullable=False)
    bio = Column(Text)
    hobbies = Column(Text)
    photo_id = Column(String(128))
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")

class Match(Base):
    """Match model for storing user matches."""
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='unique_match'),
    )

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_matches")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_matches")

class Confession(Base):
    """Confession model for storing user confessions."""
    __tablename__ = "confessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(ConfessionStatus), default=ConfessionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="confessions")

class Report(Base):
    """Report model for storing user reports."""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('reporter_id', 'reported_id', name='unique_report'),
    )

    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="sent_reports")
    reported = relationship("User", foreign_keys=[reported_id], back_populates="received_reports")

class DailyLimit(Base):
    __tablename__ = "daily_limits"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_count = Column(Integer, default=0)
    confession_count = Column(Integer, default=0)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_daily_limit'),
    )

    # Relationships
    user = relationship("User") 