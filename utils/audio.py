from mutagen.mp3 import MP3
def calculate_duration(path: str) -> int:
    return int(MP3(path).info.length)
