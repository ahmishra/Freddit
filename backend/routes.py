# Imports
from flask_login.utils import logout_user
from backend import app, db
from flask import redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask import render_template, request
from backend.forms import LoginForm, SignupForm, NewSubfreddit
from backend.models import User, Subfreddit, Post, Comment, IPAddresses
from flask_login import login_user, login_required, current_user











# HOME
@app.route("/")
def home():
    try:
        db.session.add(IPAddresses(ip_addr=str(request.remote_addr)))
        db.session.commit()
        unique_views = list(set(IPAddresses.query.with_entities(IPAddresses.ip_addr).all()))
        views = list(IPAddresses.query.with_entities(IPAddresses.ip_addr).all())
        
    except:
        db.session.rollback()
        unique_views = list(set(IPAddresses.query.with_entities(IPAddresses.ip_addr).all()[0]))
        views = list(IPAddresses.query.with_entities(IPAddresses.ip_addr).all()[0])
        
    posts = Post.query.order_by(Post.date_posted).all()[::-1] 
    return render_template("home.html", posts=posts, views=views, unique_views=unique_views)



"""
ACTUAL FREDDIT
"""
# List subfreddits
@app.route("/subfreddits")
def subfreddits():
    return render_template("subfreddits.html", subfreddits=Subfreddit.query.all())


# New subfreddit
@login_required
@app.route("/new/subfreddit", methods=["GET", "POST"])
def new_subfreddit():
    form = NewSubfreddit()
    if form.validate_on_submit():
        if Subfreddit.query.filter_by(name=form.name.data).first():
            flash("It seems like, this subfreddit already exists!", "danger")
            return redirect(url_for("new_subfreddit"))
            
        new_subfreddit = Subfreddit(owner=current_user, name=form.name.data, description=form.description.data, banner=form.picture.data.filename)
        db.session.add(new_subfreddit)
        db.session.commit()
        flash(f"Whoo-Hoo! the subfreddit {new_subfreddit.name} was created!", "success")
        return redirect(url_for("subfreddits"))
    
    return render_template("new-subfreddit.html", form=form)


# Join subfreddit
@login_required
@app.route("/f/<subfreddit_title>/<action>")
def join_subfreddit(subfreddit_title, action):
    if action == "join":
        subfreddit = Subfreddit.query.filter_by(name=subfreddit_title).first()
        subfreddit.joined.append(current_user)
    if action == "leave":
        subfreddit = Subfreddit.query.filter_by(name=subfreddit_title).first()
        subfreddit.joined.remove(current_user)
        
    db.session.commit()  
    
    return redirect(request.referrer)


# Subfreddit info
@app.route("/f/<subfreddit_title>/")
def subfreddit_detail(subfreddit_title):
    subfreddit = Subfreddit.query.filter_by(name=subfreddit_title).first()
    posts = Post.query.filter_by(subfreddit=subfreddit).order_by(Post.date_posted)[::-1]
    
    return render_template("subfreddit-detail.html", subfreddit=subfreddit, posts=posts)


# New post
@login_required
@app.route("/new/post", methods=["GET", "POST"])
def new_post():
    if current_user.joined == []:
        flash("You must join a subfreddit before posting!", "danger")
        return redirect(url_for("subfreddits"))
    
    if request.method == "POST":
        new_post = Post(title=request.form["name"], content=request.form["content"], thumbnail=request.form["thumbnail"], subfreddit=Subfreddit.query.filter_by(name=request.form["subfreddit"]).first(), owner=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash(f"Post was created in subreddit, {Subfreddit.query.filter_by(name=request.form['subfreddit']).first().name}", "success")
        return redirect(url_for("subfreddit_detail", subfreddit_title=Subfreddit.query.filter_by(name=request.form['subfreddit']).first().name))
        
    return render_template("new-post.html")


# Post detail
@app.route("/f/<subfreddit_title>/<post_title>/")
def post_detail(subfreddit_title, post_title):    
    post = Post.query.filter_by(subfreddit=Subfreddit.query.filter_by(name=subfreddit_title).first(), title=post_title).first()
    comments = Comment.query.order_by(Comment.date_posted).all()[::-1] 
    
    return render_template("post-detail.html", post=post, comments=comments)


# New comment
@app.route("/f/<subfreddit_title>/<post_title>/comment", methods=["GET", "POST"])
def comment(subfreddit_title, post_title):
    post = Post.query.filter_by(subfreddit=Subfreddit.query.filter_by(name=subfreddit_title).first(), title=post_title).first()

    if request.method == "POST":
        comment = Comment(owner=current_user, post=post, content=request.form["content"])
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for("post_detail", subfreddit_title=subfreddit_title, post_title=post_title))
    
    return render_template("comment.html", post=post)










"""
USER AUTHENTICATION
"""

# LOGOUT
@login_required
@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out, have a great one!", "warning")
    return redirect(url_for("home"))


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f"Welcome back, {user.username.capitalize()}!", "success")
                return redirect(url_for("home"))
            
        flash("Invalid username or password.", "warning")
    
    return render_template("login.html", form=form)


# SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    form = SignupForm()
    
    if form.validate_on_submit():
        hashed_pwd = generate_password_hash(form.password.data, method="sha256")
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        flash(f"Good job, {new_user.username}! Now lets get you logged in!", "success")
        return redirect(url_for("login"))
    
    return render_template("signup.html", form=form)
