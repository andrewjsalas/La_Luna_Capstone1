from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

"""Connect to database"""


def connect_db(app):
    with app.app_context():
        db.app = app
        db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    collection = db.relationship('Collection', backref='user')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.name}>"

    @classmethod
    def register(cls, username, name, password):
        """Register user"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode("utf-8")

        user = User(
            username=username,
            name=name,
            password=hashed_pwd
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Validate user exists and correct password"""

        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


class Collection(db.Model):
    __tablename__ = 'collection'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id')
    )

    release_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    year = db.Column(db.String(4), nullable=True)
    thumbnail = db.Column(db.String(200), nullable=False)
