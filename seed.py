#beerme

import model
import csv
# from datetime import date, time, datetime


def load_users(session):     
    with open('seed_data/u.users') as data:
        reader = csv.reader(data, delimiter='|')  
        for row in reader: 
            user = model.User(id=row[0], email=row[1], password=row[2],\
                username=row[3], age=row[4], city=row[5], state=row[6])
            session.add(user)  


def load_beers(session):
    with open('seed_data/u.beers') as data:
        reader = csv.reader(data, delimiter='|')
        for row in reader:
            beer = model.Beer(id=row[0], name=row[1], brewer=row[2],\
                origin=row[3], style=row[4], abv=row[5], link=row[6],\
                image=row[7])
            session.add(beer)


def load_ratings(session):
    with open('seed_data/u.ratings') as data:
        reader = csv.reader(data, delimiter='|')
        for row in reader:
            rating = model.Rating(user_id=row[0], beer_id=row[1],\
                rating=row[2])
            session.add(rating)


def main(session):
    load_users(session)
    load_beers(session)
    load_ratings(session)
    session.commit()


if __name__ == "__main__":
    s= model.session()
    main(s)