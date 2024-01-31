# models.py

# In Flask, a models.py file is commonly used to define the database models for a Flask application, especially when using an ORM (Object-Relational Mapping) library like SQLAlchemy or Django's ORM. 

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model): # class User(db.Model): This line defines a new model named User, which will correspond to a table in the database.
    id = db.Column(db.Integer, primary_key=True) # id, username, email: These are the columns of the User table.
    fullname = db.Column(db.String(18), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __init__(self, password, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model): # class Post(db.Model): This line defines a new model named Post, which will correspond to a table in the database.
    id = db.Column(db.Integer, primary_key=True) # id, title, user_id: These are the columns of the User table.
    title = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))