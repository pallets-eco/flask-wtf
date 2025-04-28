from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from wtforms import TextAreaField
from wtforms.validators import DataRequired

from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField

DEBUG = True
SECRET_KEY = "secret"

# keys for localhost. Change as appropriate.

RECAPTCHA_PUBLIC_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
RECAPTCHA_PRIVATE_KEY = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"

app = Flask(__name__)
app.config.from_object(__name__)


class CommentForm(FlaskForm):
    comment = TextAreaField("Comment", validators=[DataRequired()])
    recaptcha = RecaptchaField()


@app.route("/")
def index(form=None):
    if form is None:
        form = CommentForm()
    comments = session.get("comments", [])
    return render_template("index.html", comments=comments, form=form)


@app.route("/add/", methods=("POST",))
def add_comment():
    form = CommentForm()
    if form.validate_on_submit():
        comments = session.pop("comments", [])
        comments.append(form.comment.data)
        session["comments"] = comments
        flash("You have added a new comment")
        return redirect(url_for("index"))
    return index(form)


if __name__ == "__main__":
    app.run()
