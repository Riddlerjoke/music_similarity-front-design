import os
from flask import Flask, render_template, request, redirect, url_for
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
BUCKET = os.getenv("BUCKET")
SHARED_SECRET_KEY = os.getenv("SHARED_SECRET_KEY")
HEADERS = {"X-Secret-Key": SHARED_SECRET_KEY}


@app.route("/")
def home():
    return redirect(url_for("list_files"))


@app.route("/list_files", methods=["POST", "GET"])
def list_files():
    list_of_mp3_files_in_s3 = requests.get(
        "http://127.0.0.1:8000/list_files"#, headers=HEADERS
    ).json()
    return render_template("list_files.html", contents=list_of_mp3_files_in_s3)


@app.route("/recommendations", methods=["POST", "GET"])
def recommendations():
    # query milvus to retrieve the embedding and metadata for the selected file
    file_path = request.args.get("file_path")
    data = {"file_path": file_path}

    response = requests.post("http://127.0.0.1:8000/query", json=data, headers=HEADERS)
    payload = response.json()

    query_embedding = payload["query_embedding"]
    query_path_band = payload["query_path_band"]
    query_artist = payload["query_artist"]
    query_album = payload["query_album"]
    query_title = payload["query_title"]
    query_top3_genres = payload["query_top3_genres"]

    # search milvus for similar songs using the query embedding
    recommendations = requests.post(
        "http://127.0.0.1:8000/search",
        json={"embedding": query_embedding},
        headers=HEADERS,
    )
    list_of_recommendations = recommendations.json()

    return render_template(
        "recommendations.html",
        query_path=query_path_band,
        query_artist=query_artist,
        query_album=query_album,
        query_title=query_title,
        query_top3_genres=query_top3_genres,
        list_of_recommendations=list_of_recommendations,
    )


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
