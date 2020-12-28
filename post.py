from flask import current_app
import re

class Song:
    def __init__(self, song_id=None, link=None, genre=None, song_name=None, artist=None):
        self.song_id = song_id
        self.link = link
        self.genre = genre
        self.song_name = song_name
        self.artist = artist
        self.embedded_link = get_embedded_link(self.link)


class Post:
    def __init__(self, post_id, date, song_id, user_id):
        self.post_id = post_id
        self.date = date
        self.song = get_song(song_id)
        self.user_id = user_id


def is_liked_by(post_id, user_id):
    db = current_app.config["db"]
    count = db.is_post_liked_by(post_id, user_id)
    return not count == 0


def get_song(song_id):
    db = current_app.config["db"]
    return db.get_song(song_id)


def get_post(post_id):
    db = current_app.config["db"]
    return db.get_post(post_id)


def create_post(user_id, song_name, link, genre, artist, date):
    db = current_app.config["db"]
    new_song = db.create_song(link, genre, song_name, artist)
    if new_song is None:
        return None
    return db.create_post(date, new_song.song_id, user_id)


def delete_post(post_id):
    db = current_app.config["db"]
    return db.delete_post(post_id)


def get_embedded_link(link):
    if "spotify" in link:
        if '/' in link:
            if '?' in link:
                link_id = re.split('/|\?', link)[-2]
            else:
                link_id = link.split('/')[-1]
        else:
            link_id = link.split(':')[-1]
        embedded_link = """https://open.spotify.com/embed/track/""" + link_id
    else:
        if "youtu.be" in link:
            link_id = link.split('/')[-1]
            if '?' in link_id:
                link_id = link_id.split('?')[0]
            if '&' in link:
                link_id = link_id.split('&')[0]
        else:
            link_id = link.split('=')[-1]
        embedded_link = """https://www.youtube.com/embed/""" + link_id
    return embedded_link
