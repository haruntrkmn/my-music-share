from flask import current_app
from flask_login import UserMixin
import database as db
import heapq


class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.active = True
        db = current_app.config["db"]
        jd = db.get_join_date(username)
        jd = jd.split(" ")
        self.join_date = jd[0] + "/" + jd[1] + "/20" + jd[2]
        gs = db.get_genre_scores(username)
        gs = gs[1:]
        self.genre_scores = gs

    def get_posts(self):
        db = current_app.config["db"]
        return db.get_posts_of_user(self.user_id)

    def get_id(self):
        return self.username

    def get_fav_genres(self):
        db = current_app.config["db"]
        genres, _ = db.get_genres()
        genres = genres.replace('(', '').replace(')', '').replace(' ', '').split(',')
        fav_genres = []
        scores = heapq.nlargest(3, self.genre_scores)
        indices = heapq.nlargest(3, list(range((len(self.genre_scores)))), key=self.genre_scores.__getitem__)
        for i in indices:
            fav_genres.append(genres[i])

        a = [fav_genres, scores]
        return a


    @property
    def is_active(self):
        return self.active


def get_indices_of_max_3_in_list(a):
    largest_3 = []
    for i in range(3):
        largest_3.append(sorted(a, reverse=True)[i])
    indices = []
    for i in largest_3:
        indices.append(a.index(i))
    return indices


def get_user(username):
    db = current_app.config["db"]
    user_id, password = db.get_user(username)
    user = User(user_id, username, password) if password else None
    if user is not None:
        user.get_fav_genres()
    return user


def create_user(username, password, join_date):
    db = current_app.config["db"]
    if db.create_user(username, password, join_date):
        user_id, _ = db.get_user(username)
        user = User(user_id, username, password)
        return user
    else:
        return None