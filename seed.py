#beerme

import model
import csv
# from datetime import date, time, datetime


def load_users(session):     
    with open('seed_data/u.users') as data:
        reader = csv.reader(data, delimiter='|')  
        for row in reader: 
            user = model.User(id=row[0], email=row[1], password=row[2],\
                name_first=row[3], name_last=row[4], age=row[5],\
                city=row[6], state=row[7])
            session.add(user)  


def load_beers(session):
    with open('seed_data/u.beers') as data:
        reader = csv.reader(data, delimiter='|')
        for row in reader:
            beer = model.Beer(id=row[0], name=row[1], brewer=row[2],\
                origin=row[3], style=row[4], abv=row[5], link=row[6])
            session.add(beer)


def load_ratings(session):
    with open('seed_data/u.ratings') as data:
        reader = csv.reader(data, delimiter='|')
        for row in reader:
            rating = model.Rating(user_id=row[0], beer_id=row[1],\
                rating=row[2], rate_time=row[3])
            session.add(rating)


def main(session):
    load_users(session)
    load_beers(session)
    load_ratings(session)
    session.commit()


if __name__ == "__main__":
    s= model.session()
    main(s)