import os
from fastapi import FastAPI, HTTPException
import uvicorn
from pymilvus import connections, Collection
import numpy as np
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

app = FastAPI(
    title="Music Recommendation System",
    description="This is a music recommendation system using FastAPI and Pydantic",
    version="1.0.0",
)

class SongPath(BaseModel):
    path: str

URI = os.getenv("MILVUS_URI")
TOKEN = os.getenv("MILVUS_TOKEN")
SHARED_SECRET_KEY = os.getenv("SHARED_SECRET_KEY")

# Connect to Milvus
try:
    connections.connect("default", uri=URI, token=TOKEN)
    print("Successfully connected to Milvus")
except Exception as e:
    print("Failed to connect to Milvus:", e)
    exit(1)

collection_512 = Collection("embeddings_512")


def get_embedding(path: str) -> Optional[List[float]]:
    # Escape single quotes in path
    path = path.replace("'", "\\'")

    query_expression = rf"path == '{path}'"
    query_result = collection_512.query(
        expr=query_expression, output_fields=["embedding"]
    )
    if not query_result:
        return None
    embedding = query_result[0]["embedding"]
    return embedding


def get_similar_songs(path: str) -> List[Dict[str, str]]:
    embedding = get_embedding(path)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Song not found")
    query_result = collection_512.search(
        data=[embedding],
        anns_field="embedding",
        param={"nprobe": 16},
        limit=10,
        offset=0,
        output_fields=["*"],
    )
    payload = []
    # create a list of dictionaries with the song's title, artist, album and path
    for song in query_result[0]:
        payload.append(
            {
                "title": song.title,
                "artist": song.artist,
                "album": song.album,
                "path": song.path,
            }
        )
    return payload


@app.post("/similar_songs")
def similar_songs(song: SongPath):
    song_list = get_similar_songs(song.path)
    return song_list


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
