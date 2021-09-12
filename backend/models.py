from backend import db
from flask_login import UserMixin
from datetime import datetime
import pytz
tz = pytz.timezone("UTC") 


# Joined
join = db.Table(
    "join",
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id")),
    db.Column("subfreddit_id", db.Integer, db.ForeignKey("subfreddit.subfreddit_id")),
)


# User Model
class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(32))
    profile = db.Column(db.String(32), nullable=False, default='profile-default.png')
    
    subfreddits = db.relationship("Subfreddit", backref="owner", lazy=True)
    posts = db.relationship("Post", backref="owner", lazy=True)
    comments = db.relationship("Comment", backref="owner", lazy=True)
    joined = db.relationship("Subfreddit", secondary=join, backref=db.backref("joined", lazy=True))
                         
    def get_id(self):
        return (self.user_id)

    def __repr__(self):
        return f"<User#{self.user_id}; USERNAME:{self.username}; EMAIL:{self.email}, PASSWORD:{self.password}>"


# Subfreddit model
class Subfreddit(db.Model):
    subfreddit_id = db.Column(db.Integer, primary_key=True, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    
    posts = db.relationship("Post", backref="subfreddit", lazy=True)
    
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(512), nullable=False)
    banner = db.Column(db.String(32), nullable=True, default='banner-default.png')
    
    def get_id(self):
        return (self.subfreddit_id)
    

# Post model
class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True, unique=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    subfreddit_id = db.Column(db.Integer, db.ForeignKey("subfreddit.subfreddit_id"))
    
    comments = db.relationship("Comment", backref="post", lazy=True)
    
    title = db.Column(db.String(32), nullable=False)
    content = db.Column(db.String(8192), nullable=False)
    thumbnail = db.Column(db.String(1024), nullable=False)
    
    date_posted = db.Column(db.String(64), nullable=False, default=datetime.now(tz).strftime("%d %b %Y, %I:%M:%S") )
    
    def get_id(self):
        return (self.post_id)


# Comment model
class Comment(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, unique=True)
    
    owner_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    subfreddit_id = db.Column(db.Integer, db.ForeignKey("subfreddit.subfreddit_id"))
    post_id = db.Column(db.Integer, db.ForeignKey("post.post_id"))

    content = db.Column(db.String(1024), nullable=True)
    date_posted = db.Column(db.String(64), nullable=False, default=datetime.now(tz).strftime("%d %b %Y, %I:%M:%S") )

    def get_id(self):
        return (self.comment_id)


# IP Addresses
class IPAddresses(db.Model):
    ip_id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    ip_addr = db.Column(db.String(128))
