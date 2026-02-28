from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

from database import SessionLocal, engine
import models

# Initialize Database
models.Base.metadata.create_all(bind=engine)

# App Setup
app = FastAPI(title="Simple Notes API", version="2.5.0", docs_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Security Vars
SECRET_KEY = "supersecretkey" # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Custom UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
        swagger_css_url="/static/custom.css"
    )

# Dependencies
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    exception = HTTPException(status_code=401, detail="Invalid credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise exception
    except JWTError: raise exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None: raise exception
    return user

# Helper Functions
def hash_password(password: str): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- ROUTES ---

@app.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="Username taken")
    new_user = models.User(username=username, hashed_password=hash_password(password))
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token({"sub": user.username}), "token_type": "bearer"}

@app.post("/notes")
def create_note(title: str, content: str, category: str = "General", user=Depends(get_current_user), db=Depends(get_db)):
    note = models.Note(title=title, content=content, category=category, owner_id=user.id)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/notes")
def get_all_notes(user=Depends(get_current_user), db=Depends(get_db)):
    return db.query(models.Note).filter(models.Note.owner_id == user.id).all()

@app.get("/notes/search")
def search_notes(query: str, user=Depends(get_current_user), db=Depends(get_db)):
    return db.query(models.Note).filter(models.Note.owner_id == user.id, models.Note.title.contains(query)).all()

@app.get("/notes/category/{cat}")
def get_by_category(cat: str, user=Depends(get_current_user), db=Depends(get_db)):
    return db.query(models.Note).filter(models.Note.owner_id == user.id, models.Note.category == cat).all()

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, user=Depends(get_current_user), db=Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.owner_id == user.id).first()
    if not note: raise HTTPException(status_code=404, detail="Not found")
    db.delete(note)
    db.commit()
    return {"message": "Deleted"}