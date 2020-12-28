import MySQLdb as dbapi2
from flask import flash
import post


class Database:
    def __init__(self, host="localhost", user="root", passwd="281898.Ts", db="mydatabase"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    def get_genres(self):
        with dbapi2.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            cursor.execute("""SHOW COLUMNS FROM genre_scores""")
            genres_ = []
            for c in cursor:
                genres_.append(c[0])

            genres_ = genres_[1:]
            if len(genres_) > 0:
                genres = "("
                zeros = "("
                for g in range(len(genres_) - 1):
                    genres += genres_[g]
                    genres += ", "
                    zeros += "0, "
                genres += genres_[len(genres_) - 1]
                genres += ")"
                zeros += "0)"

            else:
                genres = "()"
                zeros = "()"

        return genres, zeros

    def create_user(self, username, password, join_date):
        # password will be passed as hashed to this function
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            genres, zeros = self.get_genres()

            try:
                # creating a new genre_scores tuple having 0 for all attributes for newly created user
                statement = """INSERT INTO genre_scores {columns} VALUES {zeros}""".format(columns=genres, zeros=zeros)
                cursor.execute(statement)  # sql injection is not possible here

                # creating a user tuple
                statement = """INSERT INTO users (username, password_, join_date, genre_score_id)
                        SELECT %s, %s, %s, MAX(genre_score_id) FROM genre_scores """
                cursor.execute(statement, (username, password, join_date))
                connection.commit()
                cursor.close()

            except dbapi2.IntegrityError:
                flash("username exists")
                connection.rollback()
                return False

            except dbapi2.DataError:
                flash("please try a shorter username")
                connection.rollback()
                return False
            except:
                flash("please try another username")
                connection.rollback()
                return False

        return True

    def get_user(self, username):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT user_id, password_ FROM users WHERE username = %s"""
            cursor.execute(statement, (username,))

            fetch = cursor.fetchall()
            if len(fetch) == 0:
                cursor.close()
                return None, None

            user_id = fetch[0][0]
            password = fetch[0][1]
            cursor.close()
            return user_id, password

    def get_username_from_user_id(self, user_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT username FROM users WHERE user_id = %s"""
            cursor.execute(statement, (user_id,))

            fetch = cursor.fetchone()

            user_name = fetch[0]
            cursor.close()
            return user_name

    def get_join_date(self, username):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT join_date FROM users WHERE username = %s"""
            cursor.execute(statement, (username,))
            fetch = cursor.fetchall()
            if len(fetch) == 0:
                cursor.close()
                return None

            join_date = fetch[0][0]
            cursor.close()
            return join_date

    def get_genre_scores(self, username):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """  SELECT * FROM genre_scores WHERE genre_score_id = 
                            (SELECT genre_score_id FROM users where username = %s);"""
            cursor.execute(statement, (username,))
            fetch = cursor.fetchall()
            if len(fetch) == 0:
                cursor.close()
                return None

            genre_scores = fetch[0]
            cursor.close()
            return genre_scores

    def create_song(self, link, genre, song_name, artist):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            try:
                if len(artist) > 0:
                    statement = """INSERT INTO songs(link, genre, song_name, artist) VALUES (%s, %s, %s, %s);"""
                    cursor.execute(statement, (link, genre, song_name, artist))
                else:
                    statement = """INSERT INTO songs(link, genre, song_name) VALUES (%s, %s, %s);"""
                    cursor.execute(statement, (link, genre, song_name))
                connection.commit()

            except dbapi2.DataError:
                cursor.close()
                flash("try shorter inputs")
                connection.rollback()
                return None
            except:
                cursor.close()
                flash("database error")
                connection.rollback()
                return None

            statement = """SELECT * FROM songs ORDER BY song_id DESC LIMIT 1;"""  # getting last row of songs table
            cursor.execute(statement)
            fetch = cursor.fetchone()
            new_song = post.Song(fetch[0], fetch[1], fetch[2], fetch[3], fetch[4])
            cursor.close()
            return new_song

    def create_post(self, post_date, song_id, user_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            try:
                statement = """INSERT INTO posts(post_date, song_id, user_id) VALUES (%s, %s, %s)"""
                cursor.execute(statement, (post_date, song_id, user_id))
                connection.commit()

            except dbapi2.DataError:
                cursor.close()
                flash("data error on database")
                connection.rollback()
                return False
            except:
                cursor.close()
                flash("database error")
                connection.rollback()
                return False

            statement = """SELECT * FROM posts ORDER BY post_id DESC LIMIT 1;"""
            cursor.execute(statement)
            fetch = cursor.fetchone()
            new_post = post.Post(fetch[0], fetch[1], fetch[2], fetch[3])
            cursor.close()
            return new_post

    def get_song(self, song_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM songs WHERE song_id = %s;"""
            cursor.execute(statement, (song_id,))
            fetch = cursor.fetchone()
            _song = post.Song(fetch[0], fetch[1], fetch[2], fetch[3], fetch[4])
            cursor.close()
        return _song

    def get_post(self, post_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM posts WHERE post_id = %s;"""
            cursor.execute(statement, (post_id,))
            fetch = cursor.fetchone()
            if not fetch:
                cursor.close()
                return False
            _post = post.Post(fetch[0], fetch[1], fetch[2], fetch[3])
            cursor.close()
        return _post

    def get_posts_of_user(self, user_id):
        posts = []
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM posts WHERE user_id = %s;"""
            cursor.execute(statement, (user_id,))
            fetch = cursor.fetchall()
            for f in fetch:
                posts.append(post.get_post(f[0]))
            cursor.close()
        return posts

    def delete_post(self, post_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """DELETE FROM comments WHERE post_id = %s;"""  # deleting comments of post
                cursor.execute(statement, (post_id,))
                statement = """DELETE FROM likes WHERE post_id = %s;"""  # deleting likes of post
                cursor.execute(statement, (post_id,))
                statement = """SELECT song_id FROM posts WHERE post_id = %s;"""  # getting song id of post
                cursor.execute(statement, (post_id,))
                song_id = cursor.fetchone()[0]
                statement = """DELETE FROM posts WHERE post_id = %s;"""    # deleting post
                cursor.execute(statement, (post_id,))
                statement = """DELETE FROM songs WHERE song_id = %s;"""  # deleting song
                cursor.execute(statement, (song_id,))
                connection.commit()
                cursor.close()
            except:
                connection.rollback()
                return False
        return True

    def update_genre_scores(self, increase, user_id, genre):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                if increase:
                    statement = "UPDATE genre_scores SET " + genre + " = " + genre + """ + 1 WHERE genre_score_id = (SELECT genre_score_id FROM 
                    users WHERE user_id = %s);"""
                else:
                    statement = "UPDATE genre_scores SET " + genre + " = " + genre + """ - 1 WHERE genre_score_id = (SELECT genre_score_id FROM 
                                        users WHERE user_id = %s);"""
                cursor.execute(statement, (user_id,))
                connection.commit()
                if not increase:  # checking if total values of genre of removed song is zero
                    statement = "SELECT SUM(" + genre + ") FROM genre_scores;"
                    cursor.execute(statement)
                    total_values_of_genre = cursor.fetchone()[0]
                    if total_values_of_genre == 0:
                        # removing genre from genre_scores table because not any songs' genre is that
                        try:
                            statement = "ALTER TABLE genre_scores DROP COLUMN " + genre + ";"
                            cursor.execute(statement)
                            connection.commit()
                        except:
                            connection.rollback()
                            return False
                cursor.close()
            except:
                connection.rollback()
                return False

        return True

    def add_new_genre(self, genre):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = "ALTER TABLE genre_scores ADD " + str(genre) + " INT DEFAULT 0"
                cursor.execute(statement)
                connection.commit()
                cursor.close()
            except:
                connection.rollback()
                return False

        return True

    def get_posts_of_a_genre(self, genre):
        posts = []
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """SELECT * FROM posts WHERE song_id in (SELECT song_id FROM songs WHERE genre=%s);"""
                cursor.execute(statement, (genre,))
                fetch = cursor.fetchall()
                for f in fetch:
                    posts.append(post.get_post(f[0]))
                cursor.close()
            except:
                flash("error")
                return None

        return posts

    def add_like(self, user_id, post_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """INSERT INTO likes(user_id, post_id) values(%s, %s);"""
                cursor.execute(statement, (user_id, post_id))
                connection.commit()
                cursor.close()
            except:
                flash("Could not like")
                flash("user id:", user_id)
                flash("post_id:", post_id)
                connection.rollback()
                return False

        return True

    def remove_like(self, user_id, post_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """DELETE FROM likes WHERE user_id=%s && post_id=%s;"""
                cursor.execute(statement, (user_id, post_id))
                connection.commit()
                cursor.close()
            except:
                flash("Could not unlike")
                flash("user id:", user_id)
                flash("post_id:", post_id)
                connection.rollback()
                return False

        return True

    def is_post_liked_by(self, post_id, user_id):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """SELECT COUNT(*) FROM likes WHERE user_id=%s && post_id=%s;"""
                cursor.execute(statement, (user_id, post_id))
                fetch = cursor.fetchone()
                count = fetch[0]
                cursor.close()
            except:
                flash("error")
                return None

        return count

    def add_comment(self, user_id, post_id, comment):
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """INSERT INTO comments(comment_text, user_id, post_id) values(%s, %s, %s);"""
                cursor.execute(statement, (comment, user_id, post_id))
                connection.commit()
                cursor.close()
            except:
                flash("Could not comment")
                flash("user id:", user_id)
                flash("post_id:", post_id)
                connection.rollback()
                return False

        return True


    def get_likers_of_post(self, post_id):
        likers = []
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """SELECT user_id FROM likes WHERE post_id = %s;"""
                cursor.execute(statement, (post_id,))
                fetch = cursor.fetchall()
                for f in fetch:
                    likers.append(f[0])
                cursor.close()
            except:
                flash("error on getting likers")
                return None

        for l in range(len(likers)):
            likers[l] = self.get_username_from_user_id(likers[l])
        return likers


    def get_comments_of_post(self, post_id):
        comments = []
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                cursor = connection.cursor()
                statement = """SELECT comment_text, user_id FROM comments WHERE post_id = %s;"""
                cursor.execute(statement, (post_id,))
                fetch = cursor.fetchall()
                for f in fetch:
                    d = {}
                    d["comment_text"] = f[0]
                    d["username"] = self.get_username_from_user_id(f[1])
                    comments.append(d)
                cursor.close()
            except:
                flash("error on getting comments")
                return None

        return comments


    # updates feed, and returns posts list
    def update_and_get_feed(self, user):  # user object
        with dbapi2.connect(charset='utf8', host=self.host, user=self.user, passwd=self.passwd, db=self.db) as connection:
            try:
                user_id = user.user_id
                cursor = connection.cursor()
                users_genres = user.get_fav_genres()
                if 0 not in users_genres[1]:
                    # step 1
                    users_genres = users_genres[0]
                    genre_1 = users_genres[0]
                    genre_2 = users_genres[1]
                    genre_3 = users_genres[2]
                    statement = """INSERT INTO feed (SELECT post_id, %s, 0, 0 FROM posts INNER JOIN songs ON 
                                    posts.song_id=songs.song_id AND (songs.genre=%s OR songs.genre=%s OR songs.genre=%s))
                                    ON DUPLICATE KEY UPDATE feed.post_id=feed.post_id;
                                    """
                    cursor.execute(statement, (user_id, genre_1, genre_2, genre_3))
                    connection.commit()

                    # step 2
                    statement = """CREATE TEMPORARY TABLE to_be_deleted(
                                                        post_id_ INT,
                                                        user_id_ INT
                                                    );"""
                    cursor.execute(statement)

                    statement = """ INSERT INTO to_be_deleted SELECT feed.post_id, feed.user_id FROM feed INNER JOIN posts ON
                                                feed.post_id = posts.post_id INNER JOIN songs on posts.song_id = songs.song_id WHERE
                                                (posts.user_id = %s AND songs.genre != %s AND songs.genre != %s AND
                                                songs.genre != %s); DELETE FROM feed WHERE (post_id, user_id) IN
                                                (SELECT post_id_, user_id_ FROM to_be_deleted);"""
                    cursor.execute(statement, (user_id, genre_1, genre_2, genre_3))

                    statement = """DROP TABLE to_be_deleted;"""
                    cursor.execute(statement)
                    connection.commit()

                    # step 3

                    statement = """ SELECT feed.post_id, feed.user_id, songs.genre FROM feed INNER JOIN posts ON feed.post_id = posts.post_id INNER JOIN songs 
                    ON posts.song_id = songs.song_id INNER JOIN users ON users.user_id = feed.user_id 
                    INNER JOIN genre_scores ON genre_scores.genre_score_id = users.genre_score_id WHERE feed.user_id = %s AND (songs.genre = %s OR songs.genre = %s OR
                    songs.genre = %s); """
                    cursor.execute(statement, (user_id, genre_1, genre_2, genre_3))
                    fetch = cursor.fetchall()
                    print("fetch:", fetch)
                    priorities = {}
                    for f in fetch:
                        key = str(f[0]) + "," + str(f[1])
                        genre = f[2]
                        fav_3_genres = user.get_fav_genres()
                        genre_score = fav_3_genres[1][fav_3_genres[0].index(genre)]
                        likes = len(self.get_likers_of_post(f[0]))
                        priority = 0.7 * genre_score + 0.3 * likes
                        priorities[key] = priority

                    for p in priorities.keys():
                        print(p, "->", priorities[p])
                        post_id = int(p.split(',')[0])
                        user_id = int(p.split(',')[1])
                        priority_ = priorities[p]

                        statement = """ UPDATE feed SET priority=%s WHERE (post_id, user_id) = (%s, %s); """
                        cursor.execute(statement, (priority_, post_id, user_id))
                        connection.commit()


                else:  # id user does not have 3 top genres (may have 2 or 1, but it is not important), just copy all posts in feed
                    statement = """INSERT INTO feed (SELECT post_id, user_id, 0, 0 FROM posts INNER JOIN songs ON 
                                    posts.song_id=songs.song_id) ON DUPLICATE KEY UPDATE feed.post_id=feed.post_id; """
                    cursor.execute(statement)


                posts = []
                statement = """SELECT posts.* FROM feed INNER JOIN posts ON feed.post_id = posts.post_id WHERE feed.user_id = %s ORDER BY feed.priority DESC;"""
                cursor.execute(statement, (user_id, ))
                fetch = cursor.fetchall()
                for f in fetch:
                    posts.append(post.get_post(f[0]))
                cursor.close()
                return posts

            except:
                print("error on updating feed!!")
                return None
