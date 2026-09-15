from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import Base, engine, get_db
import numpy as np

# Import the standalone detector module (initializes FER detector)
import moodfeed_detector
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
	"""Accept an uploaded image (JPEG/PNG) and return detected expressions.

	Uses `moodfeed_detector.detector` to run FER on the uploaded frame and
	returns a list of detected faces with their dominant expression + confidence.
	"""
	contents = await file.read()
	# Decode image bytes to OpenCV image
	try:
		arr = np.frombuffer(contents, np.uint8)
		img = moodfeed_detector.cv2.imdecode(arr, moodfeed_detector.cv2.IMREAD_COLOR)
		if img is None:
			raise ValueError("Could not decode image")
	except Exception as exc:
		raise HTTPException(status_code=400, detail=f"Invalid image data: {exc}")

	# Run detector
	try:
		results = moodfeed_detector.detector.detect_emotions(img)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Detection error: {exc}")

	out = []
	for face in results:
		box = face.get("box", None)
		emotions = face.get("emotions", {})
		label, confidence = moodfeed_detector.dominant_expression(emotions) if emotions else (None, 0.0)
		out.append({"box": box, "label": label, "confidence": float(confidence), "emotions": emotions})

	return {"status": "ok", "faces": out}

