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
import forms
import random
from forms import LoginForm, RegistrationForm, AddBeerForm


app = Flask(__name__)
app.secret_key = "obligatory_secret_key"

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view="login"


@app.teardown_request
def close_session(exception = None):
	model.session.remove()


@login_manager.user_loader
def load_user(id):
	return model.session.query(model.User).get(id)


# if logged in, sends to "home" page, but if not logged in, send to login page
@app.route("/", methods = ['GET'])
@login_required
def index():
	return redirect(url_for("home_display"))


# to login
@app.route("/login", methods=["GET", "POST"])
def login():
	form = LoginForm(request.form)
	return render_template("login.html", form=form)


#to authenticate/login user
@app.route("/user_login", methods=["GET", "POST"])
def user_login():
	form = LoginForm(request.form)
	if request.method == "POST" and form.validate():
		find_user = model.session.query(model.User).filter_by(email=form.email.data, password=form.password.data).first()
		if find_user: 
			login_user(find_user)
			return redirect(url_for('home_display'))
	return render_template("login.html", form=form)


# register new account, part 1 of 2
@app.route("/register", methods=["GET", "POST"])
def register():
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		user = model.User()
		user.username = form.username.data
		user.email = form.email.data
		user.password = form.password.data
		user.age = form.age.data
		user.city = form.city.data
		user.state = form.state.data
		model.session.add(user)
		model.session.commit()
		return redirect(url_for('new_user'))
	return render_template('register.html', form=form)


# get more user info for account, part 2 of 2
@app.route("/new_user", methods = ["GET", "POST"])
def new_user():
	all_beers = model.session.query(model.Beer).all()
	rando_list = random.sample(range(len(all_beers)), 10)
	
	beers = []
	for i in rando_list:
		beer = model.session.query(model.Beer).filter_by(id=i).first()
		beername = beer.name
		beerimage = beer.image
		beers.append((beername, beerimage))

	rando_beers = zip(rando_list, beers) # list of tuple pairs

	return render_template('user_info.html', rando_beers=rando_beers)


# enter user preferences into database
@app.route("/user_info", methods = ["GET", "POST"])
def user_info():
	enter_rating = request.form['new_rating']
	print enter_rating
	# beer = model.session.query(model.Beer).get(id)
	# rating_change = request.form['new_rating']
	# current_rating = model.session.query(model.Rating).filter(model.Rating.user_id==current_user.id, model.Rating.beer_id==beer.id).first()
	# if current_rating:
	# 	current_rating.rating = rating_change
	# else:
	# 	new_rating = request.form['new_rating']
	# 	add_rating = model.Rating(user_id = current_user.id, beer_id = beer.id, rating = new_rating)
	# 	model.session.add(add_rating)
	# 	model.session.commit()
	# 	return redirect(url_for("beer_profile", id=beer.id))
	# model.session.commit()
	# return redirect(url_for("beer_profile", id=beer.id))



	# form = AddBeerForm(request.form)
	# if request.method == 'POST' and form.validate():
	# 	beer = model.Beer()
	# 	beer.name = form.name.data
	# 	beer.brewer = form.brewer.data
	# 	beer.origin = form.origin.data
	# 	beer.style = form.style.data
	# 	beer.abv = form.abv.data
	# 	beer.link = form.link.data
	# 	beer.image = form.image.data
	# 	model.session.add(beer)
	# 	model.session.commit()

	# 	new_beer = model.session.query(model.Beer).filter(model.Beer.name == form.name.data).first()
	# 	add4 = model.Rating(user_id = 4, beer_id = new_beer.id, rating = 1)
	# 	add5 = model.Rating(user_id = 5, beer_id = new_beer.id, rating = 2)
	# 	add6 = model.Rating(user_id = 6, beer_id = new_beer.id, rating = 3)
	# 	add7 = model.Rating(user_id = 7, beer_id = new_beer.id, rating = 4)
	# 	add8 = model.Rating(user_id = 8, beer_id = new_beer.id, rating = 5)
	# 	model.session.add(add4)
	# 	model.session.add(add5)
	# 	model.session.add(add6)
	# 	model.session.add(add7)
	# 	model.session.add(add8)
	# 	model.session.commit()
	# 	return redirect(url_for("all_beers"))
	# return render_template('new_beer.html', form=form)







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
		beernames.append((beer.name, beer.image))
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
		beerimage = beer.image
		predictions.append((prediction, beername, beerid, mod_prediction, beerimage))
	high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
	best_five = itertools.islice(high_prediction, 0, 5)

	# whoa, i can't believe i wrote all that
	return render_template("home.html", user_name=username, userid=userid,\
		high_averages=high_five, most_rated=popular_five, high_pred = best_five)


# show user profile with how many tasted, beer queue, highest rated, and recently tasted
@app.route("/profile", methods = ["GET", "POST"])
@login_required
def user_profile():
	user_name = current_user.username
	user_id = current_user.id
	all_ratings = model.session.query(model.Rating).filter_by(user_id=current_user.id).\
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
		beerimage = beer.image
		predictions.append((prediction, beername, beerid, mod_prediction, beerimage))
	high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
	best_five = itertools.islice(high_prediction, 0, 5)

	return render_template("user_profile.html", high_rated = high_rated, \
	count = how_many, user_name = user_name, userid=user_id,\
	high_pred = best_five)


# see all in user beer queue
@app.route("/profile/queue", methods = ["GET", "POST"])
@login_required
def user_queue():
	user_name = current_user.username
	user_id = current_user.id
	user_queue = model.session.query(model.Rating).filter_by(user_id=current_user.id, rating=0).all()
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
		beerimage = beer.image
		predictions.append((prediction, beername, beerid, mod_prediction, beerimage))
	high_queue = sorted(predictions, key=operator.itemgetter(0), reverse = True)

	all_ratings = model.session.query(model.Rating).filter_by(user_id=current_user.id).\
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
		beerimage = beer.image
		other_predictions.append((prediction, beername, beerid, mod_prediction, beerimage))
	high_prediction = sorted(other_predictions, key=operator.itemgetter(0), reverse = True)
	best_five = itertools.islice(high_prediction, 0, 5)
	print best_five

	return render_template("user_queue.html", user_name = user_name, \
		queue=high_queue, high_pred = best_five, count = how_many, userid=user_id)


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
			beerimage = beer.image
			predictions.append((prediction, beername, beerid, mod_prediction, beerimage))
		high_prediction = sorted(predictions, key=operator.itemgetter(0), reverse = True)
		best_five = itertools.islice(high_prediction, 0, 5)

		return render_template("user_ratings.html", user_name = user_name, \
			ratings=user_ratings, count = how_many, not_rated = not_rated,\
			high_pred = best_five, userid=user_id)


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
		top_twenty = itertools.islice(high_prediction, 0, 20)

		return render_template("user_predictions.html", user_name = user_name, \
			ratings=user_ratings, count = how_many, not_rated = not_rated,\
			high_pred = top_twenty, userid=user_id)


# show all beers in database
@app.route("/beers", methods = ["GET"])
@login_required
def all_beers():
	userid = current_user.id
	alphabetical = model.session.query(model.Beer).order_by(model.Beer.name).all()
	return render_template("all_beers.html", alphabetical=alphabetical, userid=userid)


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
		return render_template("all_beers.html", by_avg=sortby_avg, userid=userid)

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
				beerimage = unrated.image
				other_predictions.append((other_prediction, beername, beerid, mod_prediction, beerimage))
	similar_five = itertools.islice(other_predictions, 0, 5)

	return render_template("beer_profile.html", beer=beer, userid=user_id,\
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


# add a beer
@app.route("/new_beer", methods=["GET", "POST"])
@login_required
def new_beer():
	form = AddBeerForm(request.form)
	if request.method == 'POST' and form.validate():
		beer = model.Beer()
		beer.name = form.name.data
		beer.brewer = form.brewer.data
		beer.origin = form.origin.data
		beer.style = form.style.data
		beer.abv = form.abv.data
		beer.link = form.link.data
		beer.image = form.image.data
		model.session.add(beer)
		model.session.commit()

		new_beer = model.session.query(model.Beer).filter(model.Beer.name == form.name.data).first()
		add4 = model.Rating(user_id = 4, beer_id = new_beer.id, rating = 1)
		add5 = model.Rating(user_id = 5, beer_id = new_beer.id, rating = 2)
		add6 = model.Rating(user_id = 6, beer_id = new_beer.id, rating = 3)
		add7 = model.Rating(user_id = 7, beer_id = new_beer.id, rating = 4)
		add8 = model.Rating(user_id = 8, beer_id = new_beer.id, rating = 5)
		model.session.add(add4)
		model.session.add(add5)
		model.session.add(add6)
		model.session.add(add7)
		model.session.add(add8)
		model.session.commit()
		return redirect(url_for("all_beers"))
	return render_template('new_beer.html', form=form)


# to logout
@app.route("/logout", methods = ["GET"])
@login_required
def logout():
	logout_user()
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.run(debug = True)