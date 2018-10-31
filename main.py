# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
#___________________________________________________________
from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345@localhost:7778/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '12345abcde'



class Blog(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	body = db.Column(db.String(120))
	owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))	

	def __init__(self, name, body, owner):
		self.name = name
		self.body = body
		self.owner = owner
		
	def is_valid(self):
		if self.name and self.body and self.user:
			return True
		else:
			return False
			
			
class User(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	blogs = db.relationship('Blog', backref='owner')
	
	def __init__(self, username, password):
		self.username = username
		self.password = password
		
	def is_valid(self):
		if self.username and self.password:
			return True
		else:
			return False




@app.before_request
def require_login():
	allowed_routes = ['login', 'signup', 'index', 'newuser', 'blog', 'single', 'goto_login', 'login', 'goto_user', 'all_users']
	if request.endpoint not in allowed_routes and 'cur_user' not in session:
		return redirect('/goto_login')
			
			
@app.route('/', methods=['POST', 'GET'])
def index():
	
	
	posts = Blog.query.all()
	return render_template('main.html',title="Blog Posts", posts=posts, error='')
	
	
@app.route('/signup', methods=['POST', 'GET'])
def signup():
	if request.method == "POST":
		new_user = request.form['username']
		new_pass = request.form['pas1']
		new_pass_2 = request.form['pas2']
	
		if new_pass != new_pass_2:
			return render_template('testt.html', title="Signup", user1=new_user, firstpassword=new_pass, pass2=" Passwords do not match!")
		if len(new_user) <= 1 or len(new_pass) <= 1 or len(new_pass_2) <= 1:
			return render_template('testt.html', title="Signup", user1=new_user, firstpassword=new_pass, pass2="Must fill out all fields.")
		else:
			new = User(new_user, new_pass)
			db.session.add(new)
			db.session.commit()
			session['cur_user'] = new.username
			return redirect('/all_users')
		

@app.route('/newuser', methods=['POST', 'GET'])
def newuser():
	if request.method == "GET":
		return render_template('testt.html', title="Signup")
		
			
@app.route('/blog', methods=['POST', 'GET'])
def new():
	if request.method == "GET":
		posts = Blog.query.all()
		if len(session['cur_user']) >=1:
			return render_template('newpost.html', title="Create A New Post")
		else:
			return render_template('main.html',title="Blog Posts", posts=posts, error1="Must be signed in!")

@app.route('/newpost', methods=['POST','GET'])
def new_post():

	owner = User.query.filter_by(username=session['cur_user']).first()

	if request.method == 'POST':
		new_blog_title = request.form['post-title']
		new_blog_body = request.form['message']
		if len(new_blog_title) <= 0 or len(new_blog_body) <= 0:
			return render_template('newpost.html', title="Create a New Post", error="Please fill out all fields")
		else:
			new_blog = Blog(new_blog_title, new_blog_body, owner)
			db.session.add(new_blog)
			db.session.commit()
			post = Blog.query.get(new_blog.id)
			return render_template('blog.html', title=str(new_blog.name), post=post)
	else:
		return render_template('newpost.html', title="Create a New Post", error="Please fill out all fields")


@app.route('/single', methods=['POST', 'GET'])
def single():
	
	post_id = request.args.get('id')
	
	if post_id:
		post = Blog.query.get(post_id)
		return render_template('blog.html', title=str(post.name), post=post)
		
@app.route('/goto_login', methods=['POST', 'GET'])
def goto_login():
	if request.method == "GET":
		return render_template('login.html', title="Login", value="")
		
@app.route('/login', methods=['POST', 'GET'])
def login():
	if request.method == "POST":
		log_user = request.form['log-user']
		log_pass = request.form['log-pass']
		login_user = User.query.filter_by(username=log_user).first()
		if len(log_user) <=1 or len(log_pass) <=1:
			return render_template('login.html', title="Login", error="You must fill out all fields.", value=log_user)
		if login_user and login_user.password == log_pass:
			session['cur_user'] = str(login_user.username)
			return render_template('newpost.html', title="Create A New Post")
		else:
			return render_template('login.html', title="login", error="Username or Password do not match our records.", value=log_user)
			
@app.route('/goto_user', methods=['POST', 'GET'])
def goto_user():
	if request.method == "GET":
		user_id = request.args.get('user')
		posts = Blog.query.filter_by(owner_id=user_id).all()
		return render_template('user_profile.html', posts=posts)
		
@app.route('/all_users', methods=['POST', 'GET'])
def all_users():
	users = User.query.all()
	return render_template('all_users.html', users=users)
		

@app.route('/logout')
def logout():
	del session['cur_user']
	return redirect('/')
	

	
	


if __name__ == '__main__':
	app.run(port="8080")