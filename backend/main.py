from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
from models import User, Post, Reaction
from schemas import PostCreate, PostOut, ReactionCreate, ReactionOut, ReactionSummary


app = FastAPI()

# Create tables on first run; comment out after DB initialized.
Base.metadata.create_all(bind=engine)

# Allow requests from the frontend dev server
app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.post("/posts", response_model=PostOut)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
	post = Post(title=payload.title, content=payload.content, author_id=payload.author_id)
	db.add(post)
	db.commit()
	db.refresh(post)
	return post


@app.post("/reactions", response_model=ReactionOut)
def create_reaction(payload: ReactionCreate, db: Session = Depends(get_db)):
	post = db.get(Post, payload.post_id)
	user = db.get(User, payload.user_id)
	if not post:
		raise HTTPException(status_code=404, detail="Post not found")
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	reaction = Reaction(emoji=payload.emoji, post_id=payload.post_id, user_id=payload.user_id)
	db.add(reaction)
	db.commit()
	db.refresh(reaction)
	return reaction


@app.get("/posts/{post_id}/reactions/summary", response_model=list[ReactionSummary])
def reactions_summary(post_id: int, db: Session = Depends(get_db)):
	rows = (
		db.query(Reaction.emoji, func.count(Reaction.id).label("count"))
		.filter(Reaction.post_id == post_id)
		.group_by(Reaction.emoji)
		.all()
	)
	return [{"emoji": r[0], "count": r[1]} for r in rows]


@app.post("/detect")
async def detect_image(file: UploadFile = File(...)):
	"""Accept an uploaded image from the frontend webcam and return a placeholder result.

	Replace the body of this function with your model inference code later.
	"""
	contents = await file.read()
	# TODO: run detection on `contents` (bytes). For now return a stub.
	return {"status": "ok", "mood": "happy", "confidence": 0.95}

