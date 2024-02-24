import datetime
import uuid
import functools
from dataclasses import asdict

from flask import Blueprint, current_app, redirect, render_template, session, request, url_for, flash
from forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
from models import Movie, User
from passlib.hash import pbkdf2_sha256

pages = Blueprint("pages", __name__, template_folder="templates", static_folder="static")


def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)
    return route_wrapper


@pages.route("/")
@login_required
def index():
    userData = current_app.db.users.find_one({"email": session["email"]})
    user = User(**userData)
    movieData = current_app.db.movies.find({"_id": {"$in": user.movies}})  # Get all movie data from database for a user
    movies = [Movie(**movie) for movie in movieData]  # List of Movie objects for each movie in movieData
    return render_template(
        "index.html",
        title="Movies Watchlist",
        movies_data=movies
    )


@pages.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):  # User already logged in
        return redirect(url_for(".index"))

    form = RegisterForm()  # Prepare RegisterForm

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data)
        )
        current_app.db.users.insert_one(asdict(user))  # Add user to DB
        flash("User registered successfully", "success")
        return redirect(url_for(".login"))
    return render_template("register.html", title="Movies Watchlist - Register", form=form)


@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        userData = current_app.db.users.find_one({"email": form.email.data})

        if not userData:  # Bad login attempt
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**userData)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):  # If login codes are correct
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="Movies Watchlist - Login", form=form)


@pages.route("/logout")
def logout():
    current_theme = session.get("theme")
    session.clear()
    session["theme"] = current_theme

    return redirect(url_for(".login"))


@pages.route("/add", methods=["GET", "POST"])
@login_required
def addMovies():
    form = MovieForm()
    if form.validate_on_submit():  # Checks whether form has been submitted and checks validation
        # Movie data object
        movie = Movie(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            director=form.director.data,
            year=form.year.data,
        )
        current_app.db.movies.insert_one(asdict(movie))
        current_app.db.users.update_one({"_id": session["user_id"]}, {"$push": {"movies": movie._id}})  # Add movies to movie list for a specific user
        return redirect(url_for(".index"))
    return render_template("newMovie.html", title="Movies Watchlist - Add Movie", form=form)  # Pass MovieForm to the template


@pages.get("/movie/<string:_id>")
def movie(_id: str):
    movieData = current_app.db.movies.find_one({"_id": _id})  # Find movie in database
    movie = Movie(**movieData)
    return render_template("movieDetails.html", movie=movie)


@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def editMovie(_id: str):
    movie = Movie(**current_app.db.movies.find_one({"_id": _id}))  # Prepare Movie data object
    form = ExtendedMovieForm(obj=movie)  # Take in movie form data
    if form.validate_on_submit():  # Upon form submission, update movie data with data from form
        movie.title = form.title.data
        movie.director = form.director.data
        movie.year = form.year.data
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data

        current_app.db.movies.update_one({"_id": movie._id}, {"$set": asdict(movie)})  # Put updated movie data into DB
        return redirect(url_for(".movie", _id=movie._id))
    return render_template("movieForm.html", movie=movie, form=form)


@pages.get("/movie/<string:_id>/rate")
@login_required
def rateMovie(_id):
    rating = int(request.args.get("rating"))  # Take movie rating and turn into an integer
    current_app.db.movies.update_one({"_id": _id}, {"$set": {"rating": rating}})  # Update rating in DB
    return redirect(url_for(".movie", _id=_id))


@pages.get("/movie/<string:_id>/watch")
@login_required
def watchToday(_id):
    current_app.db.movies.update_one({"_id": _id}, {"$set": {"last_watched": datetime.datetime.today()}})
    return redirect(url_for(".movie", _id=_id))


# DARK MODE / LIGHT MODE
@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))
