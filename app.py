import os
from flask import Flask, render_template, request, flash, redirect, session, g, abort, Response, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import check_password_hash
from werkzeug.exceptions import Unauthorized, BadRequest
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
import requests
import random
import discogs_client
from lock import API_TOKEN
from models import db, connect_db, User, Collection
from forms import LoginForm, RegisterForm, UserEditForm
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


CURR_USER_KEY = "curr_user"

app = Flask(__name__)
migrate = Migrate(app, db)
bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///recordshopdb"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "password123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

"""Connect to database"""
with app.app_context():
    connect_db(app)
    db.create_all()

"""Set discogs client token"""
d = discogs_client.Client('my_user_agent/1.0', user_token=API_TOKEN)


@app.before_request
def add_user_to_g():
    """If user logged in, add curr user to Flask global"""

    g.user = None

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    # else:
    #     g.user = None

    if CURR_USER_KEY in session:
        print(session[CURR_USER_KEY])


def do_login(user):
    """Login user"""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout User"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


########### USER SIGNUP / LOG IN / LOG OUT ROUTES ###########
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        password = form.password.data

        new_user = User.register(
            username=username, name=name, password=password)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash('Username already taken')
            return redirect('/signup')

        session[CURR_USER_KEY] = new_user.id
        do_login(new_user)
        return redirect(f"/users/profile/{new_user.id}")

    return render_template('/users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login"""

    form = LoginForm()

    if form.validate_on_submit():
        name = form.username.data
        pwd = form.password.data

        user = User.query.filter_by(username=name).first()

        if user and bcrypt.check_password_hash(user.password, pwd):
            do_login(user)
            return redirect("/")

        else:
            form.username.errors = ["Invalid username or password"]

    return render_template("/users/login.html", form=form)


@app.route('/logout')
def logout():
    """Handle user logout"""

    do_logout()

    flash("You have successfully logged out.", 'success')
    return redirect('/login')

# HOMEPAGE AND ERROR ROUTES ##########


@app.route('/', methods=['GET', 'POST'])
def homepage():
    """Render homepage"""

    """Search Bar Functionality"""
    results = None

    if request.method == 'POST':
        query = request.form['query']
        search_results = d.search(query, type='release')

        results = []
        for result in search_results.page(1):
            results.append({
                'title': result.title,
                'year': result.year,
                'thumbnail': result.thumb if result.thumb else 'https://via.placeholder.com/150x150.png?text=No+Image'
            })

    """Featured releases"""
    """The featured releases are taken from the label_id of Capitol Records and displayed"""

    featured = None

    if request.method == 'GET':
        label = d.label(654)
        feat_releases = label.releases.page(2)

        featured = []
        for release in feat_releases:
            featured.append({
                'title': release.title,
                'year': release.year,
                'thumbnail': release.thumb if release.thumb else 'https://via.placeholder.com/150x150.png?text=No+Image'
            })

    return render_template('home.html', results=results, featured=featured)


########### USER ROUTES ###########


@app.route('/users/profile/<int:user_id>')
def user_profile(user_id):
    """Show user profile"""

    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)


@app.route('/user/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user_profile(user_id):
    """Update user profile"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data,
            user.email = form.email.data,
            user.name = form.name.data

            db.session.commit()
            return redirect(f"/users/{user.id}")
        flash("Wrong password, please try again.", "danger")

    return render_template('users/edit.html', form=form, user_id=user_id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user"""

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    do_logout()
    db.session.delete(g.user)
    db.session.commit()

    return redirect('/')


@app.route('/users/collection/<int:user_id>')
def user_collection(user_id):
    "Show users collection"
    user = User.query.get_or_404(user_id)

    return render_template('users/collection.html', user=user, user_id=user_id)


##### WISHLIST AND RELEASE ROUTES #####


@app.route('/collection/<int:release_id>/add', methods=['POST'])
def add_to_collection(release_id):

    if not g.user:
        flash("Access unauthorized. Please sign in or make an account.", "danger")
        return redirect('/')

    release_id = request.form['release_id']
    title = request.form['title']
    year = request.form['year']
    thumbnail = request.form['thumbnail']

    release = d.release(release_id)

    collection_item = Collection(
        user_id=g.user.id,
        release_id=release_id,
        title=release.title,
        year=release.year,
        thumbnail=release.thumb if release.thumb else 'https://via.placeholder.com/150x150.png?text=No+Image'
    )

    db.session.add(collection_item)
    db.session.commit()

    flash('Release added to Collection.', "success")
    return redirect('/')
