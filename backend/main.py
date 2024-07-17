import json
from typing import List
from fastapi import FastAPI, HTTPException, status, UploadFile, File, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from pymongo import ReturnDocument

# Connecting to Mongo.
DATABASE_URL = "mongodb://admin:admin@mongo:27017/"
DATABASE_NAME = "database"

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust as needed
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Function to establish database connection
async def get_database():
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client[DATABASE_NAME]
    try:
        yield db
    finally:
        client.close()

# Model of Show
class Show(BaseModel):
    id: str
    title: str
    status: str
    current_episode: int

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}

# Update and Creation models
class ShowCreate(BaseModel):
    title: str
    status: str
    current_episode: int

class ShowUpdate(BaseModel):
    title: str
    status: str
    current_episode: int

# Dependency function to inject database connection into endpoints
def get_db(db: AsyncIOMotorClient = Depends(get_database)):
    return db[DATABASE_NAME]

# Endpoint to create an empty list of shows
@app.post("/create-shows-list/", status_code=status.HTTP_201_CREATED)
async def create_shows_list(db = Depends(get_db)):
    # Delete existing shows
    await db.shows.delete_many({})
    return {"detail": "Empty shows list created"}

# Existing endpoint to create a new show
@app.post("/shows/", response_model=Show, status_code=status.HTTP_201_CREATED)
async def create_show(show: ShowCreate, db = Depends(get_db)):
    existing_show = await db.shows.find_one({"title": show.title})
    if existing_show:
        raise HTTPException(status_code=400, detail="Show with this title already exists")

    show_dict = show.dict()
    result = await db.shows.insert_one(show_dict)
    show_dict["id"] = str(result.inserted_id)
    return show_dict

# Existing endpoint to import shows from a JSON file
@app.post("/import/", status_code=status.HTTP_201_CREATED)
async def import_shows(file: UploadFile = File(...), db = Depends(get_db)):
    content = await file.read()
    shows_dict = json.loads(content)
    
    await db.shows.delete_many({})

    for show_data in shows_dict:
        show_data["_id"] = ObjectId(show_data["id"])
        await db.shows.replace_one({"_id": show_data["_id"]}, show_data, upsert=True)

    return {"detail": "Shows imported successfully"}

# Existing endpoint to export shows to a JSON file
@app.get("/export/")
async def export_shows(db = Depends(get_db)):
    shows = await db.shows.find().to_list(None)
    for show in shows:
        show["id"] = str(show.pop("_id"))

    with open("shows.json", "w") as f:
        json.dump(shows, f, indent=4)

    return FileResponse("shows.json", media_type="application/json", filename="shows.json")

# Existing endpoint to read a show
@app.get("/shows/{show_id}", response_model=Show)
async def read_show(show_id: str, db = Depends(get_db)):
    try:
        # Validate show_id format
        if not ObjectId.is_valid(show_id):
            raise HTTPException(status_code=400, detail="Invalid show ID format")

        show = await db.shows.find_one({"_id": ObjectId(show_id)})
        if not show:
            raise HTTPException(status_code=404, detail="Show not found")

        show["id"] = str(show.pop("_id"))
        return show
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Existing endpoint to read shows
@app.get("/shows/", response_model=List[Show])
async def read_shows(skip: int = 0, limit: int = 10, db = Depends(get_db)):
    shows = await db.shows.find().skip(skip).limit(limit).to_list(limit)
    for show in shows:
        show["id"] = str(show.pop("_id"))
    return shows

# Existing endpoint to update a show
@app.put("/shows/{show_id}", response_model=Show)
async def update_show(show_id: str, show: ShowUpdate, db = Depends(get_db)):
    try:
        existing_show = await db.shows.find_one({"title": show.title, "_id": {"$ne": ObjectId(show_id)}})
        if existing_show:
            raise HTTPException(status_code=400, detail="Show with this title already exists")

        show_dict = show.dict()
        updated_show = await db.shows.find_one_and_update(
            {"_id": ObjectId(show_id)},
            {"$set": show_dict},
            return_document=ReturnDocument.AFTER
        )
        if not updated_show:
            raise HTTPException(status_code=404, detail="Show not found")

        updated_show["id"] = str(updated_show.pop("_id"))
        return updated_show
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Existing endpoint to delete a show
@app.delete("/shows/{show_id}", response_model=Show)
async def delete_show(show_id: str, db = Depends(get_db)):
    try:
        show = await db.shows.find_one_and_delete({"_id": ObjectId(show_id)})
        if not show:
            raise HTTPException(status_code=404, detail="Show not found")
        
        show["id"] = str(show.pop("_id"))
        return show
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
