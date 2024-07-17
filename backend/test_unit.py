import json
import os
from tempfile import NamedTemporaryFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Response, status, UploadFile, File
from fastapi.responses import FileResponse

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Pydantic models
class ShowBase(BaseModel):
    title: str
    status: str
    current_episode: int

class Show(ShowBase):
    id: int

    class Config:
        orm_mode = True

class ShowCreate(BaseModel):
    title: str
    status: str
    current_episode: int

class ShowUpdate(BaseModel):
    status: str
    current_episode: int

# SQLAlchemy model
class DBShow(Base):
    __tablename__ = "shows"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String)
    current_episode = Column(Integer)

# FastAPI setup
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shows/", response_model=Show, status_code=status.HTTP_201_CREATED)
def create_show(show: ShowCreate, db: Session = Depends(get_db)):
    db_show = DBShow(**show.dict())
    db.add(db_show)
    db.commit()
    db.refresh(db_show)
    return Show(**db_show.__dict__)

@app.get("/shows/{show_id}", response_model=Show)
def read_show(show_id: int, db: Session = Depends(get_db)):
    db_show = db.query(DBShow).filter(DBShow.id == show_id).first()
    if db_show is None:
        raise HTTPException(status_code=404, detail="Show not found")
    return db_show

@app.get("/shows/", response_model=List[Show])
def read_shows(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    shows = db.query(DBShow).offset(skip).limit(limit).all()
    return shows

@app.put("/shows/{show_id}", response_model=Show)
def update_show(show_id: int, show: ShowUpdate, db: Session = Depends(get_db)):
    db_show = db.query(DBShow).filter(DBShow.id == show_id).first()
    if db_show is None:
        raise HTTPException(status_code=404, detail="Show not found")
    for key, value in show.dict().items():
        setattr(db_show, key, value)
    db.commit()
    db.refresh(db_show)
    return db_show

@app.delete("/shows/{show_id}", response_model=Show)
def delete_show(show_id: int, db: Session = Depends(get_db)):
    db_show = db.query(DBShow).filter(DBShow.id == show_id).first()
    if db_show is None:
        raise HTTPException(status_code=404, detail="Show not found")
    db.delete(db_show)
    db.commit()
    return db_show

@app.get("/export/")
def export_shows(db: Session = Depends(get_db)):
    shows = db.query(DBShow).all()
    shows_dict = [show.__dict__ for show in shows]
    for show in shows_dict:
        show.pop('_sa_instance_state', None)
    
    with open("shows.json", "w") as f:
        json.dump(shows_dict, f, indent=4)
    
    response = FileResponse("shows.json", media_type="application/json")
    response.headers["Content-Disposition"] = "attachment; filename=shows.json"
    
    return response

@app.post("/import/")
def import_shows(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()
    shows_dict = json.loads(content)
    
    for show_data in shows_dict:
        show = db.query(DBShow).filter(DBShow.id == show_data["id"]).first()
        if not show:
            new_show = DBShow(**show_data)
            db.add(new_show)
        else:
            for key, value in show_data.items():
                setattr(show, key, value)
    
    db.commit()
    return {"detail": "Shows imported successfully"}

# Ensure tables are created
Base.metadata.create_all(bind=engine)

# Test setup
client = TestClient(app)

# Helper functions
def create_show(title, status, current_episode):
    response = client.post("/shows/", json={"title": title, "status": status, "current_episode": current_episode})
    assert response.status_code == 201
    return response.json()["id"]

def show_exists(show_id):
    response = client.get(f"/shows/{show_id}")
    return response.status_code == 200

# Unit tests
def test_create_show():
    show_id = create_show("Test Show", "watching", 1)
    assert show_exists(show_id)

def test_read_show():
    # Create a show first
    show_id = create_show("Test Show", "watching", 1)

    # Read the created show
    read_response = client.get(f"/shows/{show_id}")
    assert read_response.status_code == 200
    retrieved_show = read_response.json()
    assert retrieved_show["id"] == show_id
    assert retrieved_show["title"] == "Test Show"
    assert retrieved_show["status"] == "watching"
    assert retrieved_show["current_episode"] == 1

def test_update_show():
    # Create a show first
    show_id = create_show("Test Show", "watching", 1)

    # Update the show
    update_response = client.put(f"/shows/{show_id}", json={"status": "completed", "current_episode": 10})
    assert update_response.status_code == 200
    updated_show = update_response.json()
    assert updated_show["id"] == show_id
    assert updated_show["status"] == "completed"
    assert updated_show["current_episode"] == 10

def test_delete_show():
    # Create a show first
    show_id = create_show("Test Show to Delete", "watching", 1)

    # Delete the show
    delete_response = client.delete(f"/shows/{show_id}")
    assert delete_response.status_code == 200
    deleted_show = delete_response.json()
    assert deleted_show["id"] == show_id
    assert deleted_show["title"] == "Test Show to Delete"

    # Ensure the show is actually deleted
    assert not show_exists(show_id), f"Show with ID {show_id} still exists but should have been deleted."

def test_export_shows():
    response = client.get("/export/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment; filename=shows.json" in response.headers["content-disposition"]

    with open("shows.json", "r") as f:
        exported_data = json.load(f)
        assert isinstance(exported_data, list)
        assert all(isinstance(show, dict) for show in exported_data)

    os.remove("shows.json")

def test_import_shows():
    # Create a temporary test_data.json file for import testing
    test_data = [
        {"id": 1, "title": "Test Show 1", "status": "watching", "current_episode": 1},
        {"id": 2, "title": "Test Show 2", "status": "completed", "current_episode": 10}
    ]
    
    with NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(json.dumps(test_data).encode('utf-8'))
        temp_file.seek(0)
        
        files = {"file": (temp_file.name, temp_file, "application/json")}
        response = client.post("/import/", files=files)
    
    os.remove(temp_file.name)  # Remove the temporary test_data.json file after import test
    
    assert response.status_code == 200
    assert "detail" in response.json()
    assert "imported successfully" in response.json()["detail"]