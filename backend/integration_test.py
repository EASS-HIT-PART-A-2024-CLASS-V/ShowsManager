import json
import os
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import pytest


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
        from_attributes = True

class ShowCreate(BaseModel):
    title: str
    status: str
    current_episode: int

class ShowUpdate(BaseModel):
    title: str
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

# Helper functions to help handling SQLite format.
@app.post("/create-shows-list/", status_code=status.HTTP_201_CREATED)
def create_shows_list(db: Session = Depends(get_db)):
    try:
        # Delete existing shows
        db.query(DBShow).delete()
        db.commit()

        return {"detail": "Empty shows list created"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/shows/", response_model=Show, status_code=status.HTTP_201_CREATED)
def create_show(show: ShowCreate, db: Session = Depends(get_db)):
    db_show = db.query(DBShow).filter(DBShow.title == show.title).first()
    if db_show:
        raise HTTPException(status_code=400, detail="Show already exists")
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
    if db.query(DBShow).filter(DBShow.title == show.title).first() and db_show.title != show.title:
        raise HTTPException(status_code=400, detail="Another show with the same title already exists")
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

@app.get("/export/", status_code=status.HTTP_200_OK)
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


@app.post("/import/", status_code=status.HTTP_201_CREATED)
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

@pytest.mark.asyncio
async def test_workflow():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Create an empty list of shows
        response = await client.post("/create-shows-list/")
        assert response.status_code == 201
        assert response.json() == {"detail": "Empty shows list created"}

        # Step 2: Create a new show
        show_data = {"title": "Test Show", "status": "watching", "current_episode": 1}
        response = await client.post("/shows/", json=show_data)
        assert response.status_code == 201
        created_show = response.json()
        assert created_show["title"] == "Test Show"
        assert created_show["status"] == "watching"
        assert created_show["current_episode"] == 1

        # Step 3: Read all shows
        response = await client.get("/shows/")
        assert response.status_code == 200
        shows = response.json()
        assert len(shows) == 1
        assert shows[0]["title"] == "Test Show"

        # Step 4: Update the show
        update_data = {"title": "Test Show", "status": "completed", "current_episode": 10}
        response = await client.put(f"/shows/{created_show['id']}", json=update_data)
        assert response.status_code == 200
        updated_show = response.json()
        assert updated_show["status"] == "completed"
        assert updated_show["current_episode"] == 10

        # Step 5: Delete the show
        response = await client.delete(f"/shows/{created_show['id']}")
        assert response.status_code == 200
        deleted_show = response.json()
        assert deleted_show["id"] == created_show["id"]

        # Step 6: Import shows from a JSON file
        shows_to_import = [
            {"id": str(created_show["id"]), "title": "Test Show", "status": "watching", "current_episode": 1},
        ]
        with open("shows.json", "w") as f:
            json.dump(shows_to_import, f)

        with open("shows.json", "rb") as f:
            response = await client.post("/import/", files={"file": ("shows.json", f, "application/json")})
        assert response.status_code == 201
        assert response.json()["detail"] == "Shows imported successfully"

        # Step 7: Export shows to a JSON file
        response = await client.get("/export/")
        assert response.status_code == 200  # Updated to check for 200 OK
        assert response.headers["content-type"] == "application/json"
        assert "attachment; filename=shows.json" in response.headers["content-disposition"]

        with open("shows.json", "r") as f:
            exported_data = json.load(f)
            assert isinstance(exported_data, list)
            assert all(isinstance(show, dict) for show in exported_data)
            assert len(exported_data) == 1

        os.remove("shows.json")  # Clean up the file


@pytest.mark.asyncio
async def test_error_handling():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create an empty list of shows
        response = await client.post("/create-shows-list/")
        assert response.status_code == 201

        # Step 1: Create a show
        show_data = {"title": "Test Show", "status": "watching", "current_episode": 1}
        response = await client.post("/shows/", json=show_data)
        assert response.status_code == 201
        created_show = response.json()

        # Step 2: Try to create a show with the same title (should fail)
        response = await client.post("/shows/", json=show_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Show already exists"

        # Step 3: Create another show with a different title
        new_show_data = {"title": "New Show", "status": "watching", "current_episode": 1}
        response = await client.post("/shows/", json=new_show_data)
        assert response.status_code == 201
        new_created_show = response.json()

        # Step 4: Try to update a show to have a duplicate title (should fail)
        update_data = {"title": "Test Show", "status": "completed", "current_episode": 10}
        response = await client.put(f"/shows/{new_created_show['id']}", json=update_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Another show with the same title already exists"
