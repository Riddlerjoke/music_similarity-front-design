import sqlite3
import logging
from typing import Tuple, List, Optional


class Song:
    def __init__(
        self,
        filename: str,
        filepath: str,
        album_folder: str,
        artist_folder: str,
        filesize: float,
        title: str,
        artist: str,
        album: str,
        year: int,
        tracknumber: int,
        genre: str,
        top_5_genres: str,
    ):
        self.filename = filename
        self.filepath = filepath
        self.album_folder = album_folder
        self.artist_folder = artist_folder
        self.filesize = filesize
        self.title = title
        self.artist = artist
        self.album = album
        self.year = year if year else None
        self.tracknumber = tracknumber if tracknumber else None
        self.genre = genre if genre else None
        self.top_5_genres = (
            top_5_genres if type(top_5_genres) == str else ", ".join(top_5_genres)
        )


class DatabaseManager:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

    def close(self):
        self.conn.close()

    def execute(self, query: str, params: Tuple = ()) -> None:
        try:
            with self.conn:
                self.conn.execute(query, params)
                self.conn.commit()
        except sqlite3.Error as e:
            logging.error(f"An error occurred: {e}")

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        try:
            with self.conn:
                return self.conn.execute(query, params).fetchone()
        except sqlite3.Error as e:
            logging.error(f"An error occurred: {e}")
            return None

    def fetchall(self, query: str, params: Tuple = ()) -> Optional[List[Tuple]]:
        try:
            with self.conn:
                return self.conn.execute(query, params).fetchall()
        except sqlite3.Error as e:
            logging.error(f"An error occurred: {e}")
            return None

    def count_songs(self) -> int:
        query = "SELECT COUNT(*) FROM songs"
        return self.fetchone(query)[0]

    def insert_song(self, song: Song) -> None:
        song_data = (
            song.filename,
            song.filepath,
            song.album_folder,
            song.artist_folder,
            song.filesize,
            song.title,
            song.artist,
            song.album,
            song.year,
            song.tracknumber,
            song.genre,
            song.top_5_genres,
        )
        query = "SELECT * FROM songs WHERE filename = ? AND filepath = ?"
        existing_song = self.fetchone(query, (song.filename, song.filepath))
        if existing_song:
            return
        query = """
            INSERT INTO songs 
            (filename, filepath, album_folder, artist_folder, filesize, title, artist, album, year, tracknumber, genre, top_5_genres) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.execute(query, song_data)

    def list_all_artists(self):
        # returns a list of all artists in alphabetical order
        query = "SELECT DISTINCT artist_folder FROM songs ORDER BY artist_folder ASC"
        return [row for row in self.fetchall(query)]

    def list_all_albums(self, artist: str):
        # returns a list of all albums in alphabetical order
        query = "SELECT DISTINCT album, album_folder FROM songs WHERE artist_folder = ? ORDER BY year ASC"
        return [row for row in self.fetchall(query, (artist,))]

    def list_album_tracks(self, artist: str, album: str):
        # returns a list of all tracks in an album
        query = "SELECT * FROM songs WHERE artist = ? AND album = ? ORDER BY tracknumber ASC"
        results = [row for row in self.fetchall(query, (artist, album))]
        if not results:
            query = "SELECT * FROM songs WHERE album = ? ORDER BY tracknumber ASC"
            results = [row for row in self.fetchall(query, (album,))]
        return results

    def get_exact_path_another_way(
        self, path: str, artist: str, album: str
    ) -> Optional[str]:
        # returns the exact path of a song
        query = "SELECT title FROM songs WHERE filename = ? AND album = ?"
        title_result = self.fetchone(query, (path, album))
        if title_result is None:
            return None
        title = title_result[0]
        query = (
            "SELECT filepath FROM songs WHERE title = ? AND album = ? AND folder = ?"
        )
        filepath_result = self.fetchone(query, (title, album, artist))
        return filepath_result[0] if filepath_result else None
