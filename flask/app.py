from models import DatabaseManager

from flask import Flask, render_template, redirect, url_for
import requests
from requests.exceptions import RequestException

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music.db"
db = DatabaseManager("music.db")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/artists")
def list_artists():
    artists = db.list_all_artists()
    return render_template("artists.html", artists=artists)


@app.route("/artist/<string:artist_name>/albums")
def list_artist_albums(artist_name):
    albums = db.list_all_albums(artist_name)
    return render_template("albums.html", albums=albums, artist_name=artist_name)


@app.route("/artist/<string:artist_name>/album/<string:album_name>")
def album_tracklist(artist_name, album_name):
    tracklist = db.list_album_tracks(artist_name, album_name)
    return render_template(
        "tracklist.html",
        tracklist=tracklist,
        artist_name=artist_name,
        album_name=album_name,
    )


@app.route("/similar_songs/<path:full_path>")
def similar_songs(full_path):
    url = "http://0.0.0.0:8000/similar_songs"
    data = {"path": full_path}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except RequestException as e:
        print(f"Request to {url} failed: {e}")
        return redirect(url_for("list_artists"))

    songs = response.json() if response.json() else []
    artist = songs[0]["artist"]
    title = songs[0]["title"]
    return render_template("songs.html", songs=songs[1:], artist=artist, title=title)



if __name__ == "__main__":
    app.run(debug=True)
