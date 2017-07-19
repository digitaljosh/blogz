from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 't4390lib8496vc'




class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % (self.title, self.body)


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username





#TODO add helper functions, clean up /home
#TODO flash messages


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():

    return render_template('login.html')


#@app.route('/index', methods=['POST', 'GET'])
#def index():


#def logout():
    # handles a POST request to /logout and redirects to /blog after deleting username
    # from session


@app.route('/', methods=['POST', 'GET'])
def index():

    '''
    route for homepage, checks against GET or POST requests, validates user input, displays applicable errors, submits info to db if no errors
    
    '''

    if request.method=='GET': # checks for GET request
        blog_id = request.args.get('id') # grabs blog id from query params
        if blog_id: # if query params exist...
            blog = Blog.query.filter_by(id=blog_id).first() # matches query param blog id with blog post in db 
            #selected_blog = Blog.query.filter_by(id=blog_id).first() 
            return render_template('index.html', blog_id=blog_id, body=blog.body, main_title=blog.title) # renders template with single blog post
        
        # if there are no query params in GET request, display ALL blogs
        blog = Blog.query.all() # gets all blog posts from db
        main_title = "Blogz" 
        return render_template('index.html', blog=blog, main_title=main_title) # renders template on /home with ALL blog posts
        
        

    error_title = "Please fill in the title"
    error_body = "Please fill in the body"

    if request.method == 'POST': # checks to see if user submitted blog post data
        
        title = request.form['title'] # grabs user input for blog title
        body = request.form['body'] # grabs user input for blog body
        if title and body != "": # checks to see if content has been entered   
            new_post = Blog(title,body) # storing blog title and body in a new variable
            db.session.add(new_post) # adding new blog post to session
            db.session.commit() # committing new blog post to db
            return redirect("/?id=" + str(new_post.id)) # redirects user to home page that only displays the newly submitted post

        if body == "": # shows error if no input for blog body
            flash('Please fill out body')
            return redirect('/newpost')

        if title == "": # shows error if no input for blog title
            flash('Please fill in the title')
            return redirect('/newpost')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    '''
    route for newpost, renders newpost template
    
    '''
# TODO: consider that a user must be authenticated and in session
#       in order to access /newpost and add a blog entry.

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()