from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # This is not an actual database field, but a high-level view
    # of the relationship between users and posts,
    # and for that reason it isn't in the database diagram.
    # This  is for user -> post queries
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # user.id:
    # model is given by its database table name, for which SQLAlchemy automatically
    # uses lowercase characters and, for multi-word model names, snake case.

    def __repr__(self):
        return '<Post {}>'.format(self.body)