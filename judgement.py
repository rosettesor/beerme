#BEERME


from flask import Flask, render_template, redirect, request, session, url_for, g
# from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
import model
app = Flask(__name__)
app.secret_key = "obligatory_secret_key"

# login_manager=LoginManager()
# login_manager.init_app(app)
# login_manager.login_view="login"

@app.teardown_request
def close_session(exception = None):
    model.session.remove()


# requests session info before each function
@app.before_request
def load_user_id():
    g.logged_in = session.get('id')

# @login_manager.user_loader
# def load_user(id):
# 	return model.session.query(model.User).get(id)


# if logged in, sends to "home" page, but if not logged in, send to login page
@app.route("/", methods = ['GET'])
# @login_required
def index():
	if g.logged_in:
		return redirect(url_for("home_display"))
	if not g.logged_in:
		return redirect(url_for("login"))


# home/welcome page for logged in user
# shows suggested beers, all highest avg rated, all most tasted, all recently rated
@app.route("/home", methods = ['GET'])
def home_display():
	if g.logged_in:
		logged_user = model.session.query(model.User).get(session['id'])
		firstname = logged_user.name_first
		return render_template("home.html", user_name=firstname)
	if not g.logged_in:
		return redirect(url_for("login"))


# to login
@app.route("/login")
def login():
	return render_template("login.html")


# if email and password do not match, retry here
@app.route("/again_login")
def again_login():
	return render_template("again_login.html")


# to authenticate user
@app.route("/login_user", methods = ["POST"])
def login_user():
	user_email = request.form['email']
	user_password = request.form['password']
	find_user = model.session.query(model.User).filter_by(email=user_email, password=user_password).first()
	if find_user:
		session['email']=user_email
		session['id']=find_user.id
		# login_user(find_user)
		return redirect("/home")    # <--- when i change this to just "/" it keeps looping back to login page. never goes to home page
	else:
		return redirect("/again_login")


# to create a new account / signup
@app.route("/new_user")
def new_user():
	# form = AddUserForm()
	# return render_template("new_user.html", form=form)
	return render_template("new_user.html")


# get user info for account, part 1 of 2
@app.route("/save_user", methods=["POST"])
def save_user():
	new_email = request.form['email']
	new_password = request.form['password']
	new_firstname = request.form['firstname']
	new_lastname = request.form['lastname']
	new_age = request.form['age']
	new_city = request.form['city']
	new_state = request.form['state']
	new_user = model.User(email=new_email, password=new_password, name_first=new_firstname,\
		name_last=new_lastname, age=new_age, city= new_city, state=new_state)
	model.session.add(new_user)
	model.session.commit()
	return redirect("/home")   

	# with wt forms
	# form = AddUserForm()
	# if form.validate_on_submit():
	# OOOOORRRRRR if request.method == "POST" and form.validate():
	# 	user = User(form.email.data, form.password.data)
	# 	model.session.add(user)
	# 	return render_template(#go to home)
	# return render_template("new_user.html", form=form)


# get more user info for account, part 2 of 2
@app.route("/user_info", methods = ["GET", "POST"])
def user_info():
	pass 
	return redirect("/home")


# show user profile with how many tasted, beer queue, highest rated, and recently tasted
@app.route("/profile/<int:id>", methods = ["GET", "POST"])
def user_profile(id):
	pass
	return render_template("user_profile.html")


# show user's beer queue in order of predicted rating
@app.route("/profile/beer_queue/<int:id>", methods = ["GET"])
def user_queue(id):
	pass
	return render_template("user_queue.html")


# show user's highest rated in order of actual rating
@app.route("/profile/highest_rated/<int:id>", methods = ["GET"])
def user_highest(id):
	pass
	return render_template("user_highest.html")


# show user's recently rated in order of most recent ratings
@app.route("/profile/recent_rated/<int:id>", methods = ["GET"])
def user_recent(id):
	pass
	return render_template("user_recent.html")


# show profile for single beer
@app.route("/beer_profile/<int:id>", methods = ["GET", "POST"])
def beer_profile(id):
	pass
	return render_template("beer_profile.html")


# @app.route("/movie/<int:id>",  methods = ["GET", "POST"])
# def view_movie(id):
# 	movie = model.session.query(model.Movie).get(id)
# 	ratings = movie.ratings
# 	rating_nums = []
# 	user_rating = None
# 	for r in ratings:
# 		if r.user_id == session['id']:
# 			user_ratingr = r
# 		rating_nums.append(r.rating)
# 	avg_rating = float(sum(rating_nums))/len(rating_nums)

# 	# prediction code: only predict if the user hasn't rated yet
# 	user = model.session.query(model.User).get(session['id'])
# 	prediction = None
# 	if not user_rating:
# 		prediction = user.predict_rating(movie)
# 		effective_rating = prediction
# 	else:
# 		effective_rating = user_rating.rating
# 	# end prediction

# 	#now including the eye's opinion
# 	the_eye = model.session.query(model.User).filter_by(email="theeye@ofjudgement.com").one()
# 	eye_rating = model.session.query(model.Rating).filter_by(user_id=the_eye.id, movie_id=movie.id).first()
# 	if not eye_rating:
# 		eye_rating = the_eye.predict_rating(movie)
# 	else:
# 		eye_rating = eye_rating.rating
# 	difference = abs(eye_rating - effective_rating)

# 	messages = [ "I suppose you don't have such bad taste after all.",
#              "I regret every decision that I've ever made that has brought me to listen to your opinion.",
#              "Words fail me, as your taste in movies has clearly failed you.",
#              "That movie is great. For a clown to watch. Idiot."]
# 	beratement = messages[int(difference)]
# 	return render_template("movie.html", movie = movie, average = avg_rating, user_rating = user_rating, prediction = prediction, beratement = beratement)


# @app.route("/my_ratings")
# def my_ratings():
# 	my_ratings = model.session.query(model.Rating).filter_by(user_id=session['id']).all()
# 	return render_template("my_ratings.html", mine = my_ratings)


# @app.route("/change_rating", methods = ["POST"])
# def change_rating():
# 	movie_change = request.form['movie_name']
# 	find_movie = model.session.query(model.Movie).filter_by(name=movie_change).first()
# 	rating_change = request.form['new_rating']
# 	current_rating = model.session.query(model.Rating).filter(model.Rating.user_id==session['id'], model.Rating.movie_id==find_movie.id).first()
# 	current_rating.rating = rating_change
# 	model.session.commit()
# 	return redirect("/my_ratings")


# @app.route("/ratings/<id>") #get all ratings by particular user id
# def user_ratings(id=None):
# 	user_ratings = model.session.query(model.Rating).filter_by(user_id=id).all()
# 	return render_template("user_ratings.html", ratings=user_ratings)


@app.route("/logout", methods = ["GET"])
def logout():
	del session['id']
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.run(debug = True)