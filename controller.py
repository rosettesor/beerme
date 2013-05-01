#BEERME
# object inventory


from flask import Flask, render_template, redirect, request, session, url_for, g
from flask.ext.login import LoginManager, current_user, login_required, login_user, logout_user
import model
import math
from math import fabs
import operator
import itertools
import os
from forms import LoginForm, RegistrationForm


app = Flask(__name__)
app.secret_key = "obligatory_secret_key"

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"
# going to want form = form for all decorators applicable


@app.teardown_request
def close_session(exception = None):
	model.session.remove()


@login_manager.user_loader
def load_user(id):
	return model.session.query(model.User).get(id)


# # using flask login / wtforms, not working yet
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm(request.form)
#     if request.method == 'POST' and form.validate():
#         # login and validate the user...
#         login_user(form.admin)
#         flash("Logged in successfully.")
#         return redirect(request.args.get("next") or url_for("index"))
#     return render_template("login.html", form=form)


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
		list_ratings = []
		for r in beer.ratings:
			if r.rating != 0:
				list_ratings.append(r)
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
		if i.rating != 0:
			rated_beers.append(i.beer_id)
	not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

	predictions = []
	for beer in not_rated:
		prediction = current_user.predict_rating(beer)
		mod_prediction = int(round(prediction))
		beername = beer.name
		beerid = beer.id
		predictions.append((prediction, beername, beerid, mod_prediction))
	high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
	best_five = itertools.islice(high_prediction, 0, 5)

	# whoa, i can't believe i wrote all that
	return render_template("home.html", user_name=username, user_id=userid,\
		high_averages=high_five, most_rated=popular_five, high_pred = best_five)


@app.route('/register', methods=['GET', 'POST'])
def register():
	username = current_user.id
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = User(form.username.data, form.email.data, form.password.data)
		model.session.add(user)
		flash('Thanks for registering')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)


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
		all_ratings = model.session.query(model.Rating).filter_by(user_id=id).\
			order_by(model.Rating.rating.desc()).all()
		
		user_ratings = []
		for r in all_ratings:
			if r.rating != 0:
				user_ratings.append(r)
		how_many = len(user_ratings)
		high_rated = itertools.islice(user_ratings, 0, 5)

		rated_beers = []
		for i in user_ratings:
			rated_beers.append(i.beer_id)
		not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

		predictions = []
		for beer in not_rated:
			prediction = current_user.predict_rating(beer)
			mod_prediction = int(round(prediction))
			beername = beer.name
			beerid = beer.id
			predictions.append((prediction, beername, beerid, mod_prediction))
		high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
		best_five = itertools.islice(high_prediction, 0, 5)

		return render_template("user_profile.html", high_rated = high_rated, \
		count = how_many, user_name = user_name, id=user_id,\
		high_pred = best_five)
	return redirect("/home")


# see all in user beer queue
@app.route("/profile/queue/<int:id>", methods = ["GET", "POST"])
@login_required
def user_queue(id):
	if id == current_user.id:
		user_name = current_user.username
		user_id = current_user.id
		user_queue = model.session.query(model.Rating).filter_by(user_id=id, rating=0).all()
		how_many = len(user_queue)
		
		in_queue = []
		for i in user_queue:
			in_queue.append(i.beer_id)
		beer_queue = model.session.query(model.Beer).filter(model.Beer.id.in_(in_queue))
		
		predictions = []
		for beer in beer_queue:
			prediction = current_user.predict_rating(beer)
			mod_prediction = int(round(prediction))
			beername = beer.name
			beerid = beer.id
			predictions.append((prediction, beername, beerid, mod_prediction))
		high_queue = sorted(predictions, key=operator.itemgetter(0), reverse = True)

		all_ratings = model.session.query(model.Rating).filter_by(user_id=id).\
			order_by(model.Rating.rating.desc()).all()
		rated_beers = []
		for i in all_ratings:
			rated_beers.append(i.beer_id)
		not_queue = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

		other_predictions = []
		for beer in not_queue:
			prediction = current_user.predict_rating(beer)
			mod_prediction = int(round(prediction))
			beername = beer.name
			beerid = beer.id
			other_predictions.append((prediction, beername, beerid, mod_prediction))
		high_prediction = sorted(other_predictions, key=operator.itemgetter(0), reverse = True)
		best_five = itertools.islice(high_prediction, 0, 5)

		return render_template("user_queue.html", user_name = user_name, \
			queue=high_queue, high_pred = best_five, count = how_many, id=user_id)


# show all of user's ratings
@app.route("/profile/ratings/<int:id>", methods = ["GET"])
@login_required
def user_ratings(id):
	if id == current_user.id:
		user_name = current_user.username
		user_id = current_user.id
		all_ratings = model.session.query(model.Rating).filter_by(user_id=id).\
			order_by(model.Rating.rating.desc()).all()
		user_ratings = []
		for r in all_ratings:
			if r.rating != 0:
				user_ratings.append(r)

		how_many = len(user_ratings)
		rated_beers = []
		for i in user_ratings:
			rated_beers.append(i.beer_id)
		not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))
		
		predictions = []
		for beer in not_rated:
			prediction = current_user.predict_rating(beer)
			mod_prediction = int(round(prediction))
			beername = beer.name
			beerid = beer.id
			predictions.append((prediction, beername, beerid, mod_prediction))
		high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
		best_five = itertools.islice(high_prediction, 0, 5)

		return render_template("user_ratings.html", user_name = user_name, \
			ratings=user_ratings, count = how_many, not_rated = not_rated,\
			high_pred = best_five, id=user_id)


# show all unrated beers, ordered by prediction
@app.route("/profile/predictions/<int:id>", methods = ["GET"])
@login_required
def user_predictions(id):
	if id == current_user.id:
		user_name = current_user.username
		user_id = current_user.id
		all_ratings = model.session.query(model.Rating).filter_by(user_id=id).\
			order_by(model.Rating.rating.desc()).all()
		all_beers = model.session.query(model.Beer).all()
		user_ratings = []
		for r in all_ratings:
			if r.rating != 0:
				user_ratings.append(r)
		how_many = ((len(all_beers))-(len(user_ratings)))

		rated_beers = []
		for i in user_ratings:
			rated_beers.append(i.beer_id)
		not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

		predictions = []
		for beer in not_rated:
			prediction = current_user.predict_rating(beer)
			mod_prediction = int(round(prediction))
			beername = beer.name
			beerid = beer.id
			predictions.append((prediction, beername, beerid, mod_prediction))
		high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)

		return render_template("user_predictions.html", user_name = user_name, \
			ratings=user_ratings, count = how_many, not_rated = not_rated,\
			high_pred = high_prediction, id=user_id)


# show all beers in database
@app.route("/beers", methods = ["GET"])
@login_required
def all_beers():
	userid = current_user.id
	alphabetical = model.session.query(model.Beer).order_by(model.Beer.name).all()
	return render_template("all_beers.html", alphabetical=alphabetical, id=userid)


@app.route("/beers_display", methods = ["GET", "POST"])
@login_required
def beers_display():
	sort_by = request.form['sort_beers']
	userid = current_user.id

	if sort_by == "brewer":
		by_brewer = model.session.query(model.Beer).order_by(model.Beer.brewer).all()
		return render_template("all_beers.html", by_brewer=by_brewer, id=userid)
	elif sort_by == "name":
		alphabetical = model.session.query(model.Beer).order_by(model.Beer.name).all()
		return render_template("all_beers.html", alphabetical=alphabetical, id=userid)
	elif sort_by == "origin":
		by_origin = model.session.query(model.Beer).order_by(model.Beer.origin).all()
		return render_template("all_beers.html", by_origin=by_origin, id=userid)
	elif sort_by == "style":
		by_style = model.session.query(model.Beer).order_by(model.Beer.style).all()
		return render_template("all_beers.html", by_style=by_style, id=userid)
	elif sort_by == "abv":
		by_abv = model.session.query(model.Beer).order_by(model.Beer.abv).all()
		return render_template("all_beers.html", by_abv=by_abv, id=userid)
	else:    # trying to arrange by average rating
		all_beers = model.session.query(model.Beer).all()
		all_ratings = []  #becomes a list of lists. each inner list has all ratings for particular beer
		for beer in all_beers:	
			list_ratings = []
			for r in beer.ratings:
				if r.rating != 0:
					list_ratings.append(r)
			all_ratings.append(list_ratings)

		id_avg = []  #stands for beer id, average
		for r in all_ratings:
			rating_nums = []
			for i in r:
				beerid = i.beer_id
				rating = i.rating
				rating_nums.append(rating)
				average = (float(sum(rating_nums))/len(rating_nums))
			id_avg.append((beerid, average))

		beernames = []
		for i in id_avg:
			beer = model.session.query(model.Beer).filter_by(id=i[0]).one()
			beernames.append(beer.name)
		id_avg_d = dict(zip(id_avg, beernames))
	
		id_avg_nm = []   #stands for beer id, average, name
		for key in id_avg_d:
			tuple1 = key[0]
			tuple2 = key[1]
			tuple3 = id_avg_d[key]
			id_avg_nm.append((tuple1, tuple2, tuple3))
	
		sortby_avg = sorted(id_avg_nm, key=operator.itemgetter(1), reverse = True)
		return render_template("all_beers.html", by_avg=sortby_avg, id=userid)

# show profile for single beer
@app.route("/beer/<int:id>", methods = ["GET", "POST"])
@login_required
def beer_profile(id):
	beer = model.session.query(model.Beer).get(id)
	user_id = current_user.id

	ratings = beer.ratings # all rating objects for a particular beer
	rating_nums = [] # create list rating_nums
	user_rating = None
	for r in ratings: # loop through each rating object in all rating objects
		if r.rating != 0:
			if r.user_id == current_user.id: # does this rating belong to this user
				user_rating = r # yes, yes it does
			rating_nums.append(r.rating)
	avg_rating = float((sum(rating_nums))/(len(rating_nums)))

	# # using list comprehension
	# ratings = model.session.query(model.Rating).\
	# 		  filter_by(beer_id=id).\
	# 	  	  filter(model.Rating.rating != 0).\
	# 	  	  all() # all rating objects for a particular beer
	# rating_nums = [ r.rating for r in ratings ]

	my_rating = None
	for x in ratings:
		if x.rating == 0 and x.user_id == current_user.id:
			my_rating = x

	# only predict if the user hasn't rated yet
	if user_rating is None or my_rating:
		not_rounded = current_user.predict_rating(beer)
		prediction = int(round(not_rounded))
	else:
		prediction = user_rating.rating
		not_rounded = user_rating.rating


	# to identify beers with similar prediction coefficients
	user_ratings = model.session.query(model.Rating).filter_by(user_id=current_user.id).all()
	rated_beers = []
	for i in user_ratings:
		if i.rating != 0:
			rated_beers.append(i.beer_id)
	not_rated = model.session.query(model.Beer).filter(~model.Beer.id.in_(rated_beers))

	other_predictions = []
	for unrated in not_rated:
		if unrated.id != beer.id:
			other_prediction = current_user.predict_rating(unrated)
			difference = fabs(other_prediction - not_rounded)
			if difference < 0.5:
				mod_prediction = int(round(other_prediction))
				beername = unrated.name
				beerid = unrated.id
				other_predictions.append((other_prediction, beername, beerid, mod_prediction))
	similar_five = itertools.islice(other_predictions, 0, 5)

	return render_template("beer_profile.html", beer=beer, user_id=user_id,\
		average=avg_rating, user_rating=user_rating, my_rating=my_rating, prediction=prediction,\
		try_five=similar_five)


@app.route("/add_queue/<int:id>", methods = ["GET", "POST"])
@login_required
def add_queue(id):
	beer = model.session.query(model.Beer).get(id)
	current_rating = model.session.query(model.Rating).filter(model.Rating.user_id==current_user.id, model.Rating.beer_id==beer.id).first()
	if current_rating:
		return redirect(url_for("beer_profile", id=beer.id))
	else:
		add_rating = model.Rating(user_id = current_user.id, beer_id = beer.id, rating = 0)
		model.session.add(add_rating)
		model.session.commit()
		return redirect(url_for("beer_profile", id=beer.id))


@app.route("/change_rating/<int:id>", methods = ["GET", "POST"])
@login_required
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

# to logout
@app.route("/logout", methods = ["GET"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.run(debug = True)