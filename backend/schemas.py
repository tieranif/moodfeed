from pydantic import BaseModel
from typing import List


class PostCreate(BaseModel):
	title: str
	content: str
	author_id: int


class PostOut(BaseModel):
	id: int
	title: str
	content: str
	author_id: int

	class Config:
		orm_mode = True


class ReactionCreate(BaseModel):
	emoji: str
	post_id: int
	user_id: int


class ReactionOut(BaseModel):
	id: int
	emoji: str
	post_id: int
	user_id: int

	class Config:
		orm_mode = True


class ReactionSummary(BaseModel):
	emoji: str
	count: int
