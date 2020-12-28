from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class PostForm(FlaskForm):
    genres = "(a, b, c, d, e, f, g)"
    song_name = StringField("Song name", validators=[DataRequired()])
    artist = StringField("Artist", validators=None)
    link = StringField("Link", validators=[DataRequired()])
    new_genre = StringField("New genre", validators=None)
    genre = RadioField('Genre', choices=genres, default=genres[0][0])
    submit1 = SubmitField("submit")


class DiscoverForm(FlaskForm):
    genres = "(a, b, c, d, e, f, g)"
    genres = genres.replace('(', '').replace(')', '').replace(' ', '').split(',')
    genres.sort()
    for g in range(len(genres)):
        genres[g] = (genres[g], genres[g])

    genre = RadioField('Genre', choices=genres, default=genres[0][0])


class Button(FlaskForm):
    pass


