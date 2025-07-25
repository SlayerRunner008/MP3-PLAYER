from fastapi import FastAPI
from config.database import engine, Base
from routes import homeRoute, songRoute, authRoute
from fastapi.staticfiles import StaticFiles
app = FastAPI(title="Songs API", version="0.0.1")

Base.metadata.create_all(bind=engine)
app.mount("/files", StaticFiles(directory="static/files"), name="files")
#app.include_router(homeRoute.router)
app.include_router(songRoute.router)
#app.inlcude_router(authRoute.router)
