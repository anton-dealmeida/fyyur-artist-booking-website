#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import array
from ctypes import addressof
import json
import re
import string
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# Connect to a local postgresql database
# This is done in the config.py and imported on line 21 using app.config.from_object('config')
# This will import settings I define there, this is a best practice for python
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class BaseModel(db.Model):
    __abstract__ = True

    def __init__(self) -> None:
        super().__init__()

    def __repr__(self) -> str:
        items = ("%s: %r" % (key, value)
                 for key, value in self.__dict__.items() if not key.startswith('_'))
        return "<%s: {%s}>" % (self.__class__.__name__, ', '.join(items))

    def detailed_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Venue(BaseModel):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Implement any missing fields, as a database migration using Flask-Migrate
    description = db.Column(db.String(), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    website = db.Column(db.String())
    genres = db.Column(db.ARRAY(db.String()))
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')

    def summarized_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}

    def dict(self) -> dict:
        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state}


class Artist(BaseModel):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # Implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(), default='')
    website = db.Column(db.String())
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def summarized_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}

    def dict(self) -> dict:
        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state}


# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(BaseModel):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('Venue.id'), primary_key=True
    )
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'), primary_key=True
    )
    start_time = db.Column(db.String(), nullable=False)

    def __init__(self, venue_id, artist_id, start_time) -> None:
        self.venue_id = venue_id
        self.artist_id = artist_id
        self.start_time = start_time

    def artist_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def venue_details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time,
        }

    def summarized_dict(self) -> dict:
        return {'id': self.id, 'name': self.start_time}

    def dict(self) -> dict:
        return {'id': self.id, 'venue_id': self.venue_id, 'artist_id': self.artist_id, 'state': self.state}


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }]

    # empty data object
    data = []
    ct = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    # get all the venues
    venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    # place holder
    venue_state_and_city = ''

    # loop through all venues and feed the upcoming shows, city, states and the venue information
    for venue in venues:
        # calculate how many shows happen after the current time
        upcoming_shows = venue.shows.filter(Show.start_time > ct).all()
        if venue_state_and_city == venue.city + venue.state:
            data[len(data) - 1]['venues'].append({
                'id': venue.id,
                'name': venue.name,
                # get number of shows
                'num_upcoming_shows': len(upcoming_shows)
            })
        else:
            venue_state_and_city == venue.city + venue.state
            data.append({
                'city': venue.city,
                'state': venue.state,
                'venues': [{
                    'id': venue.id,
                    'name': venue.name,
                    'num_upcoming_events': len(upcoming_shows)
                }]
            })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }

    query = Venue.query.filter(Venue.name.ilike(
        '%' + request.form['search_term'] + '%'
    ))

    venues = list(map(Venue.summarized_dict, query))
    response = {
        "count": len(venues),
        "data": venues
    }

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    data1 = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": [{
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [{
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }

    ct = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    query = Venue.query.get(venue_id)

    if query:
        data = Venue.detailed_dict(query)

        shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(
            Show.venue_id == venue_id).filter(Show.start_time > ct).all()

        upcoming_shows = list(map(Show.artist_details, shows_query))
        data['upcoming_shows'] = upcoming_shows
        data['upcoming_shows_count'] = len(upcoming_shows)
        print(data)

        shows_query = Show.query.options(db.joinedload(Show.Venue)).filter(
            Show.venue_id == venue_id).filter(Show.start_time <= ct).all()

        past_shows = list(map(Show.artist_details, shows_query))
        data['past_shows'] = past_shows
        data['past_shows_count'] = len(past_shows)
        print(data)

        return render_template('pages/show_venue.html', venue=data)
    return render_template('errors/404.html'), 404

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # Insert form data as a new Venue record in the db, instead
    # Modify data to be the data object returned from db insertion
    try:
        venue = Venue(
            name=request.form['name'],
            genres=request.form.getlist('genres'),
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website_link'],
            facebook_link=request.form['facebook_link'],
            image_link=request.form['image_link'],
            seeking_talent='seeking_talent' in request.form,
            description=request.form['seeking_description'],
        )

        Venue.insert(venue)
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    except Exception as e:
        db.session.rollback()
        # On unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')


@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    # Replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]

    data = Artist.query.all()

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }

    query = Artist.query.filter(Artist.name.ilike(
        '%'+request.form['search_term']+'%'))
    artists = list(map(Artist.summarized_dict, query))
    response = {
        'count': len(artists),
        'data': artists
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Shows the artist page with the given artist_id
    # Replace with real artist data from the artist table, using artist_id
    data1 = {
        "id": 1,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 2,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [],
        "upcoming_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] ==
                artist_id, [data1, data2, data3]))[0]

    ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = Artist.query.get(artist_id)

    if artist_id:
        data = Artist.detailed_dict(query)
        data['genres'] = re.split(",", data['genres'], flags=re.IGNORECASE)
        shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(
            Show.artist_id == artist_id).filter(Show.start_time > ct).all()
        shows_list = list(map(Show.venue_details, shows_query))
        data['upcoming_shows'] = shows_list
        data['upcoming_shows_count'] = len(shows_list)

        # reusing existing variables to keep memory profile low
        shows_query = Show.query.options(db.joinedload(Show.Artist)).filter(
            Show.artist_id == artist_id).filter(Show.start_time <= ct).all()
        shows_list = list(map(Show.venue_details, shows_query))
        data['past_shows'] = shows_list
        data['past_shows_count'] = len(shows_list)

        return render_template('pages/show_artist.html', artist=data)
    return render_template('errors/404.html'), 404

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 1,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }

    artist = Artist.query.get(artist_id)

    if artist:
        details = Artist.detailed_dict(artist)
        form.name.data = details['name']
        form.genres.data = details['genres']
        form.city.data = details['city']
        form.city.data = details['city']
        form.state.data = details['state']
        form.phone.data = details['phone']
        form.website_link.data = details['website']
        form.facebook_link.data = details['facebook_link']
        form.seeking_venue.data = details['seeking_venue']
        form.seeking_description.data = details['seeking_description']
        form.image_link.data = details['image_link']
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        print(f'Artist with id {artist_id} could not be found.')
    # Populate form with fields from artist with ID <artist_id>
    return render_template('errors/404.html'), 404


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    data = Artist.query.get(artist_id)
    if data:
        if form.validate():
            seeking_venue = False
            seeking_description = ''

            if 'seeking_venue' in request.form:
                seeking_venue = request.form['seeking_venue'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(data, 'name', request.form['name'])
            setattr(data, 'genres', request.form.getlist('genres'))
            setattr(data, 'city', request.form['city'])
            setattr(data, 'state', request.form['state'])
            setattr(data, 'phone', request.form['phone'])
            setattr(data, 'website', request.form['website'])
            setattr(data, 'facebook_link', request.form['facebook_link'])
            setattr(data, 'image_link', request.form['image_link'])
            setattr(data, 'seeking_description', seeking_description)
            setattr(data, 'seeking_venue', seeking_venue)

            Artist.update(data)
            return redirect(url_for('show_artist'), artist_id=artist_id)
        else:
            print(form.errors)

    return render_template('errors/404.html'), 404


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # Populate form with values from venue with ID <venue_id>
    query = Venue.query.get(venue_id)
    if query:
        data = Venue.detailed_dict(query)
        form.name.data = data['name']
        form.genres.data = data['genres']
        form.address.data = data['address']
        form.address.data = data['address']
        form.city.data = data["city"]
        form.state.data = data["state"]
        form.phone.data = data["phone"]
        form.website_link.data = data["website"]
        form.facebook_link.data = data["facebook_link"]
        form.seeking_talent.data = data["seeking_talent"]
        form.seeking_description.data = data["description"]
        form.image_link.data = data["image_link"]
        return render_template('forms/edit_venue.html', form=form, venue=data)
    else:
        print(f'Venue with id {venue_id} not found.')
    return render_template('errors/404.html'), 404


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    data = Venue.query.get(venue_id)

    if data:
        if form.validate():
            seeking_talent = False
            seeking_description = ''
            if 'seeking_talent' in request.form:
                seeking_talent = request.form['seeking_talent'] == 'y'
            if 'seeking_description' in request.form:
                seeking_description = request.form['seeking_description']
            setattr(data, 'name', request.form['name'])
            setattr(data, 'genres', request.form.getlist('genres'))
            setattr(data, 'address', request.form['address'])
            setattr(data, 'city', request.form['city'])
            setattr(data, 'state', request.form['state'])
            setattr(data, 'phone', request.form['phone'])
            setattr(data, 'website', request.form['website_link'])
            setattr(data, 'facebook_link', request.form['facebook_link'])
            setattr(data, 'image_link', request.form['image_link'])
            setattr(data, 'seeking_description', seeking_description)
            setattr(data, 'seeking_talent', seeking_talent)

            Venue.update(data)
            return redirect(url_for('show_venue', venue_id=venue_id))
        else:
            print(form.errors)
    return render_template('errors/404.html'), 404

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # Insert form data as a new Venue record in the db, instead
    # Modify data to be the data object returned from db insertion
    try:
        seeking_venue = False
        seeking_description = ''
        if 'seeking_venue' in request.form:
            seeking_venue = request.form['seeking_venue'] == 'y'
        if 'seeking_description' in request.form:
            seeking_description = request.form['seeking_description']
        artist = Artist(
            name=request.form['name'],
            genres=request.form['genres'],
            city=request.form['city'],
            state=request.form['state'],
            phone=request.form['phone'],
            website=request.form['website'],
            image_link=request.form['image_link'],
            facebook_link=request.form['facebook_link'],
            seeking_venue=seeking_venue,
            seeking_description=seeking_description,
        )
        Artist.insert(artist)
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!')
    except SQLAlchemyError as e:
        flash('An error occurred. Artist ' +
              request.form['name'] + 'could not be listed. ')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    query = Show.query.options(db.joinedload(
        Show.Venue), db.joinedload(Show.Artist)).all()
    data = list(map(Show.artist_details, query))
    return render_template('pages/shows.html', shows=data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():

    # called to create new shows in the db, upon submitting new show listing form
    # Insert form data as a new Show record in the db, instead
    try:
        show = Show(
            venue_id=request.form['venue_id'],
            artist_id=request.form['artist_id'],
            start_time=request.form['start_time'],
        )
        Show.insert(show)
        # on successful db insert, flash success
        flash('Show was successfully listed!')

    except SQLAlchemyError as e:
        # On unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        print(e)
        flash('An error occurred. Show could not be listed.')

    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
