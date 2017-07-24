from flask import request, redirect, render_template, session, flash
from app import app, db
from models import User, Blog
from hashutils import check_pw_hash

#TODO add helper functions, clean up /home
#TODO flash messages


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'all_posts', 'logout', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/logout', methods=['POST'])
def logout():

    '''
    handles POST request and redirects to /blog 
    after deleting username from session
    '''
    
    del session['username']
    flash('logged out')
    return redirect('/blog')


def not_valid_length(username, password):
    if username == "" or password == "":
        return True
    if len(username) < 3 or len(password) < 3:
        return True

def not_valid_match(password, verify):
    if password != verify:
        return True

def is_existing_user(username):
    db_username_count = User.query.filter_by(username=username).count()
    if db_username_count > 0:
        return True


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    '''
    If 'POST' request, validate/authorize user, commit user to DB and add to session.
    If "GET' request, display signup template.
    '''

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not_valid_length(username, password):
            flash("username/password too short")
            return redirect('/signup')
        if not_valid_match(password, verify):
            flash("passwords don't match")
            return redirect('/signup')
        if is_existing_user(username):
            flash("username already taken")
            return redirect('/signup')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['username'] = user.username
        return redirect('/newpost')


    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():

    '''
    if POST request: validate/authorize user and add user to session, redirect to /newpost
    '''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist')

    return render_template('login.html')



@app.route('/blog', methods=['GET', 'POST'])
def all_posts():

    '''
    Checks query params: 
    if 'id' found, display individual blog post
    if 'user' found, display all posts by user
    if no query params, display all blog posts from all users
    '''
        
    if "id" in request.args:
        blog_id = request.args.get('id') # <<< How does this get 'id'???
        if blog_id: 
            blog = Blog.query.filter_by(id=blog_id).first() 
            return render_template('all_blogs.html', blog=blog)
    
    if "user" in request.args:
        owner_id = request.args.get('user')   # <<< How does this get 'user'???
        blogs = Blog.query.filter_by(owner_id=owner_id).all()
        one_post = Blog.query.filter_by(owner_id=owner_id).first()
        return render_template('singleUser.html', blogs=blogs, one_post=one_post)


    blogs = Blog.query.all()
    users = User.query.all() 
    return render_template('all_blogs.html', blogs=blogs, users=users, main_title="Blogz Posts")
    


@app.route('/', methods=['POST', 'GET'])
def index():

    '''
    If 'GET' requests, validates user input, displays applicable errors, submits info to db if no errors
    '''
        
    # display ALL users
    users = User.query.all()
    return render_template('index.html', users=users, main_title="Blogz Users") 


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    '''
    If 'POST' request, validate input, commit to DB, display new post.
    If 'GET' request, display newpost template.
    '''

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if len(title) < 1:
            flash('Please enter a title')
            return redirect('/newpost')
        if len(body) < 2:
            flash('Please enter body')
            return redirect('/newpost')
        blog = Blog(title=title,body=body,owner=owner)
        db.session.add(blog)
        db.session.commit()
        url = '/blog?id=' + str(blog.id)
        return redirect(url)

    return render_template('newpost.html', main_title="Add a Blog Post")



if __name__ == '__main__':
    app.run()