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
    allowed_routes = ['login', 'signup', 'index', 'all_posts', 'logout']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout', methods=['POST'])
def logout():
    # handles a POST request to /logout and redirects to /blog after deleting username
    # from session
    del session['username']
    flash('logged out')
    return redirect('/')




@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if len(username) < 3 or len(password) < 3:
            flash("username/password too short")
            return redirect('/signup')
        if password != verify:
            flash("passwords don't match")
            return redirect('/signup')
        db_username_count = User.query.filter_by(username=username).count()
        if db_username_count > 0:
            flash("username already taken")
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect('/newpost')


    # if input is validated and authorized store user in session and redirect to "/newpost"

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():

    # if GET request display login.html
    # if POST request, validate and authorize and add user to session and redirect to /newpost

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')



@app.route('/blog', methods=['GET'])
def all_posts():
    # display links (home, all posts, new post, login, logout)
    # display "blog posts!" with a list of all posts
    # posts are displayed as Title-body-written by username
    # Title links to individual post at /blog?id=[blog_id]
    # username links to page of all users posts /blog?user=[username] (use singUser.html template to render)

    
    blog = Blog.query.all() # gets all blog posts from db
    return render_template('index.html', blog=blog, main_title="Blogz Posts")




    


@app.route('/', methods=['POST', 'GET'])
def index():

    '''
    route for homepage, checks against GET or POST requests, validates user input, displays applicable errors, submits info to db if no errors
    
    '''

    # render index.html for this route 
    # display links (home, all posts, new post, login, logout)
    # display "blog users!" with a list of all users
    # users listed are links that direct to /blog?user=[user]

    if request.method=='GET': # checks for GET request
        user_id = request.args.get('id') # grabs blog id from query params
        if user_id: # if query params exist...
            user = User.query.filter_by(id=user_id).first() # matches query param blog id with blog post in db
            blogs = Blog.query.filter_by(id=user_id).all() 
            return render_template('singleUser.html', user=user, blogs=blogs)


        
    # display ALL users
    users = User.query.all() # gets all blog posts from db
    #main_title="Blogz Users"
    return render_template('index.html', users=users, main_title="Blogz Users") # renders template on / with ALL blog posts
        
        

    #error_title = "Please fill in the title"
    #error_body = "Please fill in the body"

    #if request.method == 'POST': # checks to see if user submitted blog post data
        
     #   title = request.form['title'] # grabs user input for blog title
      #  body = request.form['body'] # grabs user input for blog body
       # if title and body != "": # checks to see if content has been entered   
        #    new_post = Blog(title,body) # storing blog title and body in a new variable
         #   db.session.add(new_post) # adding new blog post to session
          #  db.session.commit() # committing new blog post to db
           # return redirect("/?id=" + str(new_post.id)) # redirects user to home page that only displays the newly submitted post

      #  if body == "": # shows error if no input for blog body
       #     flash('Please fill out body')
        #    return redirect('/newpost')

        #if title == "": # shows error if no input for blog title
         #   flash('Please fill in the title')
          #  return redirect('/newpost')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    '''
    route for newpost, renders newpost template
    
    '''

# display links (home, all posts, etc)
# display 'new post' with inputs for 'title' and 'post' (body) and 'submit' button
# after 'submit' redirect to individual post /blog?id=[blog_id]

    return render_template('newpost.html', main_title="Add a Blog Post")



if __name__ == '__main__':
    app.run()