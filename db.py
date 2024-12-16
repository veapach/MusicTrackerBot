from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

engine = create_engine("sqlite:///subscriptions.db")
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)

    subscriptions = relationship("Subscription", back_populates="user")


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    last_release_date = Column(DateTime, nullable=True)

    subscriptions = relationship("Subscription", back_populates="artist")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    artist_id = Column(Integer, ForeignKey("artists.id"))

    user = relationship("User", back_populates="subscriptions")
    artist = relationship("Artist", back_populates="subscriptions")

    __table_args__ = (
        UniqueConstraint("user_id", "artist_id", name="unique_subscription"),
    )


Base.metadata.create_all(bind=engine)
