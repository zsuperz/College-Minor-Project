# from flask import <thing> is a way of importing specific components, classes, functions, or variables from the flask module.

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import secrets
from flask_bcrypt import Bcrypt


# Load environment variables

load_dotenv()


#In Flask, the statement app = Flask(__name__) is used to create an instance of the Flask class, which represents your web application. 

app = Flask(__name__)

bcrypt = Bcrypt(app)

# app.config in Flask is a dictionary-like object used for storing the configuration variables of your Flask application.

# Use environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mkv'}

# Your database configuration here


# it check files that are allowed to upload from [ALLOWED_EXTENSIONS] variable.

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# it is user class also connected to database.
# it stores users info.

class User(db.Model): # class User(db.Model): This line defines a new model named User, which will correspond to a table in the database.
    id = db.Column(db.Integer, primary_key=True) # id, username, email: These are the columns of the User table.
    fullname = db.Column(db.String(18), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def create_post(self, content):
        post = Post(content=content, user_id=self.id)
        db.session.add(post)
        db.session.commit()

# it is post class also connected to database.
# it stores post info.
                
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    media_filename = db.Column(db.String(255), nullable=True)

# it is comment class also connected with database.
# it stores comment info.
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    

# The @app.route("/") syntax in Flask is a decorator used for associating a specific URL with a view function in your Flask application. 

@app.route("/")
def hello_world():
    return render_template('frontpage.html')


# signup form backend.

@app.route('/signup', methods=['GET', 'POST'])
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form['fullname']  # information in the signup form.
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(fullname=fullname, email=email, username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login')) # after filling signup info it shows login page.
    return render_template('signup.html')


# login form backend.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'] # information in the login form.
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        
        if user and bcrypt.check_password_hash(user.password, password): # if user login info match with saved data base info it says Login successful.
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful', 'success')
            return redirect(url_for('view_posts')) # after successful login it shows view_post html page / feed page.
        else:
            flash('Login failed. Please check your username and password.', 'danger') # if the login info wrong or does not match it shows this message.

    return render_template('login.html') # it shows login page.


# feed / all post backend.

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    # Handle new post creation
    return "New post page"

@app.route('/posts')
def view_posts():
    posts = Post.query.all()
    for post in posts:
        print(f"Post Title: {post.title}")
    return render_template('post.html', posts=posts)

    

# login to create post backend.

@app.route('/create_post', methods=['GET'])
def show_create_post_form():
    # Show the create post form
    if 'user_id' not in session:  # if user not logged in it shows this.
        flash('You need to be logged in to create a post.', 'danger')
        return redirect(url_for('login')) # it shows login page.
    
    return render_template('create_post.html') # it shows create post page.


# create post form backend.

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user_id' not in session:
        flash('You need to be logged in to create a post.', 'danger')
        return redirect(url_for('login')) # if user not logged in it shows this.

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user:
        title = request.form.get('post_title', '') # it is create post form info.
        content = request.form.get('post_content', '')
        
        # Handle file upload
        if 'post_media' in request.files:
            media_file = request.files['post_media']

            if media_file and allowed_file(media_file.filename):
                filename = secure_filename(media_file.filename)
                media_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # it saves post file image/video in the folder.
                post = Post(title=title,content=content, user_id=user.id, media_filename=filename)
                db.session.add(post)
                db.session.commit()
                flash('Post created successfully!', 'success') # after creating post it shows this message.
            else:
                flash('Invalid file type. Allowed types: png, jpg, jpeg, gif, mp4, avi, mkv', 'danger') # if file type invalid it shows this.
        else:
            flash('Media file not provided.', 'danger') # if the media file not provided it shows this.
    else:
        flash('User not found.', 'danger') # if the user not logged in or dont have account it shows this.

    return redirect(url_for('view_posts')) # after creating post it shows feed.

# logout backend.

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully.', 'success') # if the user click on logout button it shows this message.
    return redirect(url_for('hello_world')) # after logout it shows login page.

# comment page backend.

@app.route('/comments/<int:post_id>', methods=['GET', 'POST'])
def view_comments(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post_id).all()

    if request.method == 'POST':
        if 'user_id' not in session:
            flash('You need to be logged in to comment.', 'danger') # if user not logged in and try to comment on post it shows this message.
            return redirect(url_for('login')) # it shows login page.

        user_id = session['user_id']
        user = User.query.get(user_id)

        if user:
            comment_content = request.form['comment_content'] # create comment form.
            new_comment = Comment(content=comment_content, user_id=user_id, post_id=post_id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment added successfully!', 'success') # if user comment on post it shows this message.
            return redirect(url_for('view_comments', post_id=post_id))
        else:
            flash('User not found.', 'danger')

    return render_template('comments.html', comments=comments, post_id=post_id) # it shows comment page.

# create comment backend.

@app.route('/create_comment/<int:post_id>', methods=['POST'])
def create_comment(post_id):
    if 'user_id' not in session:
        flash('You need to be logged in to comment.', 'danger') # if user try to comment and not logged in it shows this message.
        return redirect(url_for('login')) # it shows login page.

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user:
        comment_content = request.form['comment_content'] # comment form.
        new_comment = Comment(content=comment_content, user_id=user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success') # if user comment on post it shows this message.
        return redirect(url_for('view_comments', post_id=post_id)) # it shows comment page.
    else:
        flash('User not found.', 'danger')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()       
    app.run(debug=False)  # The debug=True argument enables debug mode, which provides useful debugging information if there are errors in your application.
                          # When not developing or the site is live this should be debug=Flase for the user friendly.  







