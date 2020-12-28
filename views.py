from flask import current_app, render_template, request, redirect, url_for, flash
from passlib.hash import pbkdf2_sha256 as hasher
from flask_login import login_user, logout_user, login_required, current_user
from wtforms import RadioField
import forms
import user as u
import post
from datetime import date


def home_page():
    return render_template("home.html")

@login_required
def feed_page():
    db = current_app.config["db"]
    posts = db.update_and_get_feed(current_user)
    embedded_links = []
    is_spotifys = []
    is_likeds = []

    for post_ in posts:
        embedded_links.append(post_.song.embedded_link)
        is_spotifys.append("spotify" in post_.song.link)
        is_likeds.append(post.is_liked_by(post_.post_id, current_user.user_id))

    return render_template("feed.html", posts=posts, embedded_links=embedded_links,
                           is_spotifys=is_spotifys, is_likeds=is_likeds)


def login_page():
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.data["username"].strip()
        user = u.get_user(username)
        if user is not None:
            password = form.data["password"].strip()
            if hasher.verify(password, user.password):
                login_user(user)
                next_page = request.args.get("next", url_for("feed_page"))
                return redirect(next_page)
        flash("Wrong username or password")
    return render_template("login.html", form=form)


@login_required
def post_page(post_id):
    form = forms.Button()
    post_ = post.get_post(post_id)
    can_delete = False
    db = current_app.config["db"]
    likers = db.get_likers_of_post(post_id)
    comments = db.get_comments_of_post(post_id)
    if current_user.user_id == post_.user_id:
        can_delete = True
    if form.is_submitted():
        if post.delete_post(post_id):
            db.update_genre_scores(increase=False, user_id=current_user.user_id, genre=post_.song.genre)

        return redirect(url_for('profile_page'))

    if not post_:
        return render_template("error.html")
    embedded_link = post_.song.embedded_link
    username = db.get_username_from_user_id(post_.user_id)
    return render_template("post.html", post=post_, can_delete=can_delete, embedded_link=embedded_link,
                           is_spotify="spotify" in post_.song.link, username=username, likers=likers, comments=comments)


def logout_page():
    logout_user()
    return redirect(url_for("login_page"))


def create_account_page():
    form = forms.LoginForm()
    if form.validate_on_submit():
        username = form.data["username"].strip()
        password = form.data["password"].strip()
        hashed = hasher.hash(password)
        today = date.today()
        forbidden = [';', '.', ',', ':', '_', '@', '#', '*', '=', '"']
        if contains(username, forbidden):
            flash("please remove non-letters from your name")
        else:
            new_user = u.create_user(username, hashed, today.strftime("%d %m %y"))
            if new_user:
                login_user(new_user)
                next_page = request.args.get("next", url_for("feed_page"))
                return redirect(next_page)
    return render_template("create_account.html", form=form)


def contains(s, f):
    for f_ in f:
        if f_ in s:
            return True
    return False


def is_number(a):
    try:
        int(a) + 0
        return True
    except:
        return False


@login_required
def discover_select_page():
    db = current_app.config["db"]
    genres, _ = db.get_genres()
    genres = genres.replace('(', '').replace(')', '').replace(' ', '').split(',')
    genres.sort()
    for g in range(len(genres)):
        genres[g] = (genres[g], genres[g])

    #dynamically changing radiofield choices
    class F(forms.DiscoverForm):
        pass

    F.genre = RadioField('Genre', choices=genres, default=genres[0][0], validators=None)
    form = F()
    if form.is_submitted():
        genre = form.data["genre"]
        next_page = request.args.get("next", url_for("discover_show_page", genre=genre))
        return redirect(next_page)

    return render_template("discover_select.html", form=form)


@login_required
def discover_show_page(genre):
    db = current_app.config["db"]
    posts = db.get_posts_of_a_genre(genre)
    embedded_links = []
    is_spotifys = []
    is_likeds = []
    for post_ in posts:
        embedded_links.append(post_.song.embedded_link)
        is_spotifys.append("spotify" in post_.song.link)
        is_likeds.append(post.is_liked_by(post_.post_id, current_user.user_id))

    return render_template("discover_show.html", genre=genre, posts=posts, embedded_links=embedded_links, is_spotifys=is_spotifys, is_likeds=is_likeds)


@login_required
def profile_page(username=None):
    db = current_app.config["db"]
    genres, _ = db.get_genres()
    genres = genres.replace('(', '').replace(')', '').replace(' ', '').split(',')

    embedded_links = []
    is_spotifys = []
    if username is None:
        visitor = False
        user_ = current_user
    else:
        visitor = True
        user_ = u.get_user(username)

    posts = user_.get_posts()
    for post in posts:
        embedded_links.append(post.song.embedded_link)
        is_spotifys.append("spotify" in post.song.link)
    return render_template("profile.html", username=user_.username, join_date=user_.join_date,
                           genre_scores=list(user_.genre_scores), posts=posts, genres=genres, embedded_links=embedded_links, is_spotifys=is_spotifys, visitor=visitor)



@login_required
def create_post_page():
    db = current_app.config["db"]
    genres, _ = db.get_genres()
    genres = genres.replace('(', '').replace(')', '').replace(' ', '').split(',')
    genres.sort()
    for g in range(len(genres)):
        genres[g] = (genres[g], genres[g])

    # dynamically changing radiofield choices
    class F(forms.PostForm):
        pass
    F.genre = RadioField('Genre', choices=genres, default=genres[0][0])
    form = F()
    if form.is_submitted():
        user_id = current_user.user_id
        song_name = form.data["song_name"].lower().strip()
        link = form.data["link"].strip()
        genre = form.data["genre"].strip()
        artist = form.data["artist"].lower().strip()
        if form.data["new_genre"]:
            genre = form.data["new_genre"].strip()
            if is_number(genre):
                flash("Please specify a non-number genre")
            else:
                genre = genre.lower()
        forbidden = [';', ',', ':', '_', '@', '#', '*', '=', '"']
        if not is_number(genre):
            if contains(genre, forbidden) or contains(song_name, forbidden) or contains(artist, forbidden):
                flash("please remove non-letters from your inputs")
            else:

                today = date.today()
                new_post = post.create_post(user_id, song_name, link, genre, artist, today.strftime("%d/%m/%y"))
                if new_post is not None:
                    db.add_new_genre(genre)
                    db.update_genre_scores(increase=True, user_id=user_id, genre=new_post.song.genre)
                    next_page = request.args.get("next", url_for("post_page", post_id=new_post.post_id))
                    return redirect(next_page)


    return render_template("create_post.html", form=form)


def update_like():
    db = current_app.config["db"]
    post_id = request.form["post_id"]
    user_id = request.form["user_id"]
    if post.is_liked_by(post_id, user_id):
        db.update_genre_scores(False, user_id, post.get_post(post_id).song.genre)
        db.remove_like(user_id, post_id)
    else:
        db.update_genre_scores(True, user_id, post.get_post(post_id).song.genre)
        db.add_like(user_id, post_id)

    return request.form["post_id"]


def add_comment():
    db = current_app.config["db"]
    post_id = request.form["post_id"]
    user_id = request.form["user_id"]
    comment = request.form["comment"]
    db.update_genre_scores(True, user_id, post.get_post(post_id).song.genre)
    db.add_comment(user_id, post_id, comment)

    return request.form["post_id"]
