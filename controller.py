#BEERME


from flask import Flask, render_template, redirect, request, session, url_for, g
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
import model
import math
import operator
import itertools
app = Flask(__name__)
app.secret_key = "obligatory_secret_key"

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"


#DONE
@app.teardown_request
def close_session(exception = None):
    model.session.remove()


#DONE
@login_manager.user_loader
def load_user(id):
	return model.session.query(model.User).get(id)


#DONE
# if logged in, sends to "home" page, but if not logged in, send to login page
@app.route("/", methods = ['GET'])
@login_required
def index():
	return redirect(url_for("home_display"))


# home/welcome page for logged in user
# shows suggested beers for user, highest avg rated, most tasted/popular
@app.route("/home", methods = ['GET'])
@login_required
def home_display():
	username = current_user.username
	userid = current_user.id

	# TO SHOW HIGHEST AVERAGE RATINGS, across all beers whether user has rated or not
	# AND MOST RATED / POPULAR BEERS
	all_beers = model.session.query(model.Beer).all()
	all_ratings = []  #becomes a list of lists. each inner list has all ratings for particular beer
	for beer in all_beers:	
		list_ratings = beer.ratings
		all_ratings.append(list_ratings)

	id_avg_ln = []  #stands for beer id, average, length
	for r in all_ratings:
		how_many = len(r)
		rating_nums = []
		for i in r:
			beerid = i.beer_id
			rating = i.rating
			rating_nums.append(rating)
			average = (float(sum(rating_nums))/len(rating_nums))
		id_avg_ln.append((beerid, average, how_many))

	beernames = []
	for i in id_avg_ln:
		beer = model.session.query(model.Beer).filter_by(id=i[0]).one()
		beernames.append(beer.name)
	id_avg_ln_nm_d = dict(zip(id_avg_ln, beernames))
	
	id_avg_ln_nm = []   #stands for beer id, average, length, name
	for key in id_avg_ln_nm_d:
		tuple1 = key[0]
		tuple2 = key[1]
		tuple3 = key[2]
		tuple4 = id_avg_ln_nm_d[key]
		id_avg_ln_nm.append((tuple1, tuple2, tuple3, tuple4))
	
	sortby_avg = sorted(id_avg_ln_nm, key=operator.itemgetter(1), reverse = True)
	high_five = itertools.islice(sortby_avg, 0, 5) #lol, high five!

	sortby_len = sorted(id_avg_ln_nm, key=operator.itemgetter(2), reverse = True)
	popular_five = itertools.islice(sortby_len, 0, 5) #popular, like the plastics... or your mom

	# TO SHOW HIGHEST PREDICTION MATCHES
	user_ratings = model.session.query(model.Rating).filter_by(user_id=userid).all()
	rated_beers = []
	for i in user_ratings:
		rated_beers.append(i.beer_id)
	not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

	# ehhhh, not sure if i want the predictions to be in whole integers,
	# inflated whole integers (rounded up), or 0.5's
	predictions = []
	for beer in not_rated:
		prediction = current_user.predict_rating(beer)
		mod_prediction = round(prediction/.5)*.5
		beername = beer.name
		beerid = beer.id
		predictions.append((prediction, beername, beerid, mod_prediction))
	high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
	best_five = itertools.islice(high_prediction, 0, 5)

	# whoa, i can't believe i wrote all that
	return render_template("home.html", user_name=username, user_id=userid,\
		high_averages=high_five, most_rated=popular_five, high_pred = best_five)

#DONE
# to login
@app.route("/login")
def login():
	return render_template("login.html")


# to authenticate user
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
    # if request.method == "POST" and "email" in request.form:
    find_user = model.session.query(model.User).filter_by(email=request.form['email'], password=request.form['password']).first()
    if login_user(find_user):
        return redirect("/home")
    return redirect("/login")


# using flask login / wtforms, not working yet
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         # login and validate the user...
#         login_user(form.admin)
#         flash("Logged in successfully.")
#         return redirect(request.args.get("next") or url_for("index"))
#     return render_template("login.html", form=form)


# to create a new account / signup
@app.route("/new_user")
def new_user():
	form = model.AddUserForm()
	return render_template("new_user.html", form=form)


# get user info for account, part 1 of 2
@app.route("/save_user", methods=["POST"])
def save_user():
	# new_email = request.form['email']
	# new_password = request.form['password']
	# new_firstname = request.form['firstname']
	# new_lastname = request.form['lastname']
	# new_age = request.form['age']
	# new_city = request.form['city']
	# new_state = request.form['state']
	# new_user = model.User(email=new_email, password=new_password, name_first=new_firstname,\
	# 	name_last=new_lastname, age=new_age, city= new_city, state=new_state)
	# model.session.add(new_user)
	# model.session.commit()
	# return redirect("/home")   

	form = model.AddUserForm()
	if form.validate_on_submit():
	# OOOOORRRRRR if request.method == "POST" and form.validate():
		user = User(email=form.email.data, password=form.password.data)
		model.session.add(user)
		model.session.commit()
		return redirect("/home")
	return render_template("new_user.html", form=form)


# get more user info for account, part 2 of 2
@app.route("/user_info", methods = ["GET", "POST"])
def user_info():
	pass 
	return redirect("/home")


# show user profile with how many tasted, beer queue, highest rated, and recently tasted
@app.route("/profile/<int:id>", methods = ["GET", "POST"])
@login_required
def user_profile(id):
	if id == current_user.id:
		user_name = current_user.username
		user_id = current_user.id
		high_rated = model.session.query(model.Rating).filter_by(user_id=id).order_by(model.Rating.rating.desc()).limit(4).all()
		user_ratings = model.session.query(model.Rating).filter_by(user_id=id).all()
		how_many = len(user_ratings)
		rated_beers = []
		for i in user_ratings:
			rated_beers.append(i.beer_id)
		not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))
		# in_queue = model.session.query(model.Rating).filter_by(user_id=id, rating=None)
		return render_template("user_profile.html", high_rated = high_rated, \
		count = how_many, user_name = user_name, id=user_id, not_rated = not_rated)
	return redirect("/home")


# show all of user's ratings
@app.route("/profile/ratings/<int:id>", methods = ["GET"])
@login_required
def user_ratings(id):
	if id == current_user.id:
		user_name = current_user.username
		user_id = current_user.id
		user_ratings = model.session.query(model.Rating).filter_by(user_id=id).\
			order_by(model.Rating.rating.desc()).all()
		how_many = len(user_ratings)
		rated_beers = []
		for i in user_ratings:
			rated_beers.append(i.beer_id)
		not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))
		return render_template("user_ratings.html", user_name = user_name, \
			ratings=user_ratings, count = how_many, not_rated = not_rated, id=user_id)


# show profile for single beer
@app.route("/beer/<int:id>", methods = ["GET", "POST"])
@login_required
def beer_profile(id):
	beer = model.session.query(model.Beer).get(id)
	user_id = current_user.id
	ratings = beer.ratings
	rating_nums = []
	user_rating = None
	for r in ratings:
		if r.user_id == current_user.id:
			user_rating = r
		rating_nums.append(r.rating)
	avg_rating = float(sum(rating_nums))/len(rating_nums)

	# prediction code: only predict if the user hasn't rated yet
	if user_rating is None:
		prediction = round((current_user.predict_rating(beer))/.5)*.5
	else:
		prediction = user_rating.rating
	# end prediction
	return render_template("beer_profile.html", beer=beer, user_id=user_id,\
		average=avg_rating, user_rating=user_rating, prediction=prediction)


@app.route("/change_rating/<int:id>", methods = ["GET", "POST"])
def change_rating(id):
	beer = model.session.query(model.Beer).get(id)
	rating_change = request.form['new_rating']
	current_rating = model.session.query(model.Rating).filter(model.Rating.user_id==current_user.id, model.Rating.beer_id==beer.id).first()
	if current_rating:
		current_rating.rating = rating_change
	else:
		new_rating = request.form['new_rating']
		add_rating = model.Rating(user_id = current_user.id, beer_id = beer.id, rating = new_rating)
		model.session.add(add_rating)
		model.session.commit()
		return redirect(url_for("beer_profile", id=beer.id))
	model.session.commit()
	return redirect(url_for("beer_profile", id=beer.id))


@app.route("/logout", methods = ["GET"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.run(debug = True)