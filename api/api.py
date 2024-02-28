import os
from fastapi import FastAPI, HTTPException, Request
import uvicorn
from collections import defaultdict
import boto3
from pymilvus import connections, Collection
import numpy as np
from pydantic import BaseModel, Field
from typing import List


class QueryModel(BaseModel):
    file_path: str = Field(..., description="The path of the file")


class SearchModel(BaseModel):
    embedding: List[float] = Field(..., description="The embedding of the file")


def load_env_vars_from_file(filepath):
    with open(filepath) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value


load_env_vars_from_file(".env")

app = FastAPI(
    title="Music Recommendation System",
    description="This is a music recommendation system using FastAPI and Pydantic",
    version="1.0.0",
)

URI = os.getenv("MILVUS_URI")
TOKEN = os.getenv("MILVUS_TOKEN")
BUCKET = os.getenv("BUCKET")
SHARED_SECRET_KEY = os.getenv("SHARED_SECRET_KEY")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("REGION")

# Connect to Milvus
connections.connect("default", uri=URI, token=TOKEN)
collection_512 = Collection("embeddings_512")

# Connect to S3
session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
s3 = session.client("s3")


def get_list_of_mp3_paths_from_s3():
    response = s3.list_objects_v2(Bucket=BUCKET)
    mp3_paths = []
    for obj in response.get("Contents", []):
        if obj["Key"].endswith(".mp3"):
            mp3_paths.append(obj["Key"])
    return mp3_paths


@app.get("/", tags=["Home"])
def home():
    """
    Home endpoint. Returns a welcome message.
    """
    return {"message": "Welcome to the Music Recommendation System"}


@app.get("/list_files", tags=["Files"])
def list_files():
    """
    Returns a list of all mp3 files in the S3 bucket, grouped by artist.
    """

    list_of_mp3_files_in_s3 = get_list_of_mp3_paths_from_s3()

    files_by_artist = defaultdict(list)
    for file in list_of_mp3_files_in_s3:
        artist = file.split("/")[2]
        files_by_artist[artist].append(file)
    list_of_mp3_files_by_artist = list(files_by_artist.values())

    return list_of_mp3_files_by_artist


@app.post("/query", tags=["Query"])
def query(model: QueryModel):
    """
    Queries the Milvus collection for a specific file and returns its metadata and embedding.
    """
    query_path = model.file_path.replace("uploads/", "")
    query_result = collection_512.query(
        expr=f'path == "{query_path}"', output_fields=["*"]
    )

    embedding_512 = query_result[0]["embedding"]
    embedding_512 = np.array(embedding_512).tolist()

    payload = {
        "query_path_band": query_path.split("/")[1],
        "query_artist": query_result[0]["artist"],
        "query_album": query_result[0]["album"],
        "query_title": query_result[0]["title"],
        "query_top3_genres": query_result[0]["top_5_genres"][:3],
        "query_embedding": embedding_512,
    }

    return payload


@app.post("/search", tags=["Search"])
def search(model: SearchModel):
    """
    Searches the Milvus collection for files similar to the given embedding and returns a list of recommendations.
    """
    search_result = collection_512.search(
        data=[model.embedding],
        anns_field="embedding",
        param={"nprobe": 16},
        limit=200,
        offset=1,
        output_fields=["*"],
    )

    list_of_recommendations = []
    already_proposed_artists = set()
    for i, result in enumerate(search_result[0]):
        if len(list_of_recommendations) >= 10:
            break
        if result.artist not in already_proposed_artists:
            already_proposed_artists.add(result.artist)
            list_of_recommendations.append(
                [
                    result.path.split("/")[1],
                    result.artist,
                    result.album,
                    result.title,
                    result.top_5_genres[:3],
                ]
            )

    return list_of_recommendations


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
