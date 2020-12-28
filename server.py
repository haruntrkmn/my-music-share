from flask import Flask
from flask_login import LoginManager
from user import get_user
import database
import views

lm = LoginManager()
lm.login_message = ""

@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


# def create_app():
#     app = Flask(__name__)
#     app.config.from_object("settings")
#     app.add_url_rule("/", view_func=views.feed_page, methods=["GET", "POST"])
#     app.add_url_rule(
#         "/login", view_func=views.login_page, methods=["GET", "POST"]
#     )
#     app.add_url_rule("/logout", view_func=views.logout_page)
#     app.add_url_rule("/feed", view_func=views.feed_page)
#     app.add_url_rule("/profile", view_func=views.profile_page, methods=["GET", "POST"])
#     app.add_url_rule("/profile/<string:username>", view_func=views.profile_page, methods=["GET", "POST"])
#     app.add_url_rule("/create_account", view_func=views.create_account_page, methods=["GET", "POST"])
#     app.add_url_rule("/post/<int:post_id>/", view_func=views.post_page, methods=["GET", "POST"])
#     app.add_url_rule("/create_post/", view_func=views.create_post_page, methods=["GET", "POST"])
#     app.add_url_rule("/create_post/<string:new_genre>", view_func=views.create_post_page, methods=["GET", "POST"])
#     app.add_url_rule("/discover_select", view_func=views.discover_select_page, methods=["GET", "POST"])
#     app.add_url_rule("/discover_show/<string:genre>", view_func=views.discover_show_page)
#     app.add_url_rule("/_update_like", view_func=views.update_like, methods=["POST"])
#     app.add_url_rule("/_add_comment", view_func=views.add_comment, methods=["POST"])
#
#     lm.init_app(app)
#     lm.login_view = "login_page"
#
#     db = database.Database()
#     app.config["db"] = db
#
#     return app
app = Flask(__name__)
if __name__ == "__main__":
    app.config.from_object("settings")
    app.add_url_rule("/", view_func=views.feed_page, methods=["GET", "POST"])
    app.add_url_rule(
        "/login", view_func=views.login_page, methods=["GET", "POST"]
    )
    app.add_url_rule("/logout", view_func=views.logout_page)
    app.add_url_rule("/feed", view_func=views.feed_page)
    app.add_url_rule("/profile", view_func=views.profile_page, methods=["GET", "POST"])
    app.add_url_rule("/profile/<string:username>", view_func=views.profile_page, methods=["GET", "POST"])
    app.add_url_rule("/create_account", view_func=views.create_account_page, methods=["GET", "POST"])
    app.add_url_rule("/post/<int:post_id>/", view_func=views.post_page, methods=["GET", "POST"])
    app.add_url_rule("/create_post/", view_func=views.create_post_page, methods=["GET", "POST"])
    app.add_url_rule("/create_post/<string:new_genre>", view_func=views.create_post_page, methods=["GET", "POST"])
    app.add_url_rule("/discover_select", view_func=views.discover_select_page, methods=["GET", "POST"])
    app.add_url_rule("/discover_show/<string:genre>", view_func=views.discover_show_page)
    app.add_url_rule("/_update_like", view_func=views.update_like, methods=["POST"])
    app.add_url_rule("/_add_comment", view_func=views.add_comment, methods=["POST"])

    lm.init_app(app)
    lm.login_view = "login_page"

    db = database.Database()
    app.config["db"] = db
    port = app.config.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port)
