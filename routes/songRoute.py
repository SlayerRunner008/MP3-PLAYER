from fastapi import Depends, APIRouter, Query, Path, UploadFile, File, Form, HTTPException
from config.database import Session as Session
from models.song import Song as SongModel
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.encoders import jsonable_encoder
from utils.audio import calculate_duration
from utils.deleteFile import deleteFilePath,getFilePath
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional
from mutagen.mp3 import MP3
from sqlalchemy import func
import os, shutil, unicodedata
load_dotenv()


def normalize(text):
    return unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII").lower().strip()

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

    filePath = getFilePath(audioFile.filename,audioFile)

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

@router.patch("/update/{songId}")
async def updateSong(
    songId: int,
    title: str = Form(...),
    author: str = Form(...),
    audioFile: UploadFile = File(...)
):
    db = Session()
    result = db.query(SongModel).filter_by(id=songId).first()
    if not result:
        db.close()
        return JSONResponse(content={"message": "not found"}, status_code=404)

    filePath = getFilePath(audioFile.filename, audioFile)

    appHost = os.environ.get("APP_HOST", "localhost")
    appPort = os.environ.get("APP_PORT", "8000")
    baseUrl = f"http://{appHost}:{appPort}"
    songUrl = f"{baseUrl}/files/{audioFile.filename}"

    if result.url != songUrl:
        deleteFilePath(result.url)

    duration = calculate_duration(filePath)

    result.title = title
    result.author = author
    result.length = duration
    result.url = songUrl
    db.commit()
    db.close()
    return JSONResponse(content={"message": "song updated!!"}, status_code=201)


@router.get("/songs/{songId}")
async def getSongById(songId: int):
    db = Session()
    song = db.query(SongModel).filter_by(id=songId).first()
    if not song:
        raise HTTPException(status_code=404, detail="No se encontró la canción")
    return JSONResponse(content=jsonable_encoder(song),status_code=200)

@router.get("/songs")
async def getSongs():
    db=Session()
    songs=db.query(SongModel).all()
    db.close()
    return JSONResponse(status_code=200,content=jsonable_encoder(songs))
