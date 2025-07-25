from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, Form
from config.database import Session as Session
from models.song import Song as SongModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from utils.audio import calculate_duration
from fastapi.staticfiles import StaticFiles
import os, shutil
from dotenv import load_dotenv

load_dotenv()

class Song(BaseModel):
    title: str = Field(max_length=100, min_length=1, default="Título de la canción")
    author: str = Field(max_length=100, min_length=1, default="Autor de la canción")
    length: Optional[int] = Field(default=None, description="Duración de la canción")
    url: Optional[str] = Field(default=None, description="Enlace al archivo de audio")

    class Config:
        orm_mode = True

router = APIRouter()

@router.post("/upload", response_model=Song)
async def uploadSong(
    audioFile: UploadFile = File(...),
    songTitle: str = Form(...),
    songAuthor: str = Form(...)
):
    db = Session()


    targetFolder = os.path.join(os.getcwd(), "static", "files")
    os.makedirs(targetFolder, exist_ok=True)
    filePath = os.path.join(targetFolder, audioFile.filename)
    with open(filePath, "wb") as buffer:
        shutil.copyfileobj(audioFile.file, buffer)


    duration = calculate_duration(filePath)
    appHost = os.environ.get("APP_HOST", "localhost")
    appPort = os.environ.get("APP_PORT", "8000")
    baseUrl = f"http://{appHost}:{appPort}"
    songUrl = f"{baseUrl}/files/{audioFile.filename}"


    newSong = SongModel(
        title=songTitle,
        author=songAuthor,
        length=duration,
        url=songUrl
    )

    try:
        db.add(newSong)
        db.commit()
        db.refresh(newSong)
    finally:
        db.close()

    return JSONResponse(content=jsonable_encoder(newSong))
