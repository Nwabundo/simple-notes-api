from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Initialize Database
models.Base.metadata.create_all(bind=engine)

# Initialize app with docs_url=None to stop the "green/blue" layout
app = FastAPI(
    title="Simple Notes API",
    description="A professional backend service for managing study notes.",
    version="1.0.0",
    docs_url=None
)

# Mount the static folder correctly
app.mount("/static", StaticFiles(directory="static"), name="static")

# Custom route to load the layout AND your pink CSS
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # We point directly to your file here:
        swagger_css_url="/static/custom.css" 
    )

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API ROUTES ---

@app.post("/notes")
def create_note(title: str, content: str, db: Session = Depends(get_db)):
    note = models.Note(title=title, content=content)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/notes")
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Note).all()

@app.get("/notes/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}")
def update_note(note_id: int, title: str, content: str, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = title
    note.content = content
    db.commit()
    db.refresh(note)
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}