from pathlib import Path
import shutil
from fastapi import UploadFile, File

BaseAudioPath = Path.cwd() / "static" /"files"
BaseAudioPath.mkdir(parents=True, exist_ok=True)
def getFilePath(fileName: str, upload: UploadFile) -> Path:
    filePath = BaseAudioPath / fileName
    with open(filePath, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)
    return filePath


def deleteFilePath(fileUrl: str) -> bool:
    try:
        fileName=fileUrl.split("/")[-1]
        filePath= BaseAudioPath / fileName
        if filePath.exists():
            filePath.unlink()
            return True
    except Exception as e:
        print(f"error deleting the file {e}")
    return False