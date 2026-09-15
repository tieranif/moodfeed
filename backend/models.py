from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
	__tablename__ = "users"
	id = Column(Integer, primary_key=True, index=True)
	username = Column(String, unique=True, index=True)

	posts = relationship("Post", back_populates="author")
	reactions = relationship("Reaction", back_populates="user")


class Post(Base):
	__tablename__ = "posts"
	id = Column(Integer, primary_key=True, index=True)
	title = Column(String, index=True)
	content = Column(Text)
	author_id = Column(Integer, ForeignKey("users.id"))

	author = relationship("User", back_populates="posts")
	reactions = relationship("Reaction", back_populates="post")


class Reaction(Base):
	__tablename__ = "reactions"
	id = Column(Integer, primary_key=True, index=True)
	emoji = Column(String, index=True)
	post_id = Column(Integer, ForeignKey("posts.id"))
	user_id = Column(Integer, ForeignKey("users.id"))

	post = relationship("Post", back_populates="reactions")
	user = relationship("User", back_populates="reactions")
