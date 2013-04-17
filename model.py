# beerme
# wtforms sites: http://pythonhosted.org/Flask-WTF/
# http://flask.pocoo.org/docs/patterns/wtforms/
# http://wtforms.simplecodes.com/docs/1.0.3/crash_course.html#displaying-errors

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
# from flask.ext.wtf import Form
# from wtforms import Textfield, validators as v
# import os
# import correlation


engine = create_engine("sqlite:///ratings.db", echo=False)
# when deploying to heroku, i think
# db_uri = os.environ.get("DATABASE_URL", "sqlite:///ratings.db")
# engine = create_engine(db_uri, echo=False) 
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()
#when rebuilding database entirely, have to do the base.metadata.create_all(engine)


class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key = True)
	email = Column(String(64), nullable=False)
	password = Column(String(64), nullable=False)
	name_first = Column(String(32), nullable=False)
	name_last = Column(String(32), nullable=False)
	age = Column(Integer, nullable=True)
	city = Column(String(20), nullable=True)
	state = Column(String(2), nullable=True)

	# for flask login
	# def is_authenticated(self):
	# 	return True

	# def is_active(self): #i.e. not paid up
	# 	return True

	# def is_anonymous(self): #usage without an account
	# 	return False

	# def get_id(self):
	# 	return unicode(self.id)


	# def similarity(self, other):
	# 	u_ratings = {}
	# 	paired_ratings = []
	# 	for r in self.ratings:
	# 		u_ratings[r.movie_id] = r

	# 	for r in other.ratings:
	# 		u_r = u_ratings.get(r.movie_id)
	# 		if u_r:
	# 			paired_ratings.append( (u_r.rating, r.rating) )

	# 	if paired_ratings:
	# 		return correlation.pearson(paired_ratings)
	# 	else:
	# 		return 0.0


	# def predict_rating(self, movie):
	# 	ratings = self.ratings
	# 	other_ratings = movie.ratings
	# 	similarities = [ (self.similarity(r.user), r) for r in other_ratings ]
	# 	similarities.sort(reverse=True)
	# 	similarities = [sim for sim in similarities if sim[0]>0]
	# 	if not similarities: 
	# 		return None
	# 	numerator = sum([r.rating * similarity for similarity, r in similarities])
	# 	denominator = sum([similarity[0] for similarity in similarities])
	# 	return numerator/denominator


class Beer(Base):
	__tablename__ = "beers"

	id = Column(Integer, primary_key = True)
	name = Column(String(64), nullable=True)
	brewer = Column(String(64), nullable=True)
	origin = Column(String(32), nullable=True)
	style = Column(String(64), nullable=True)
	abv = Column(Integer, nullable=True)
	link = Column(String(64), nullable=True)


class Rating(Base):
	__tablename__ = "ratings"

	id = Column(Integer, primary_key = True)
	beer_id = Column(Integer, ForeignKey('beers.id'))
	user_id = Column(Integer, ForeignKey('users.id'))
	rating = Column(Integer, nullable=True)
	rate_time = Column(Integer, nullable=True)

	# import time first, then time.strftime("%a, %d %b %Y %H:%M:%S +0000",\
	# time.localtime(epoch)) Replace time.localtime with time.gmtime for GMT time.

	user = relationship("User", backref=backref("ratings", order_by=id))
	beer = relationship("Beer", backref=backref("ratings", order_by=id))

# class AddUserForm(Form):
# 	email = TextField("email", validators=[v.required()])
# 	password = TextField("password", validators=[v.required()])


def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
