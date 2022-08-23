#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import array
from ctypes import addressof
import json
import re
import string
from tracemalloc import start
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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

    # convers entire model to a dictionary
    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


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
    genres = db.Column(db.String())
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

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(BaseModel):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    venue_id = db.Column(
        db.Integer,
        db.ForeignKey('Venue.id'), primary_key=True
    )
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey('Artist.id'), primary_key=True
    )
    start_time = db.Column(db.String(), nullable=False)

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
    data = []

    # query can do most of the heavy lifting, need to just massage data
    # https://stackoverflow.com/a/72432220
    # output in answer above doesn't work, needed a new forloop
    # added order_by for good measure to keep the data returned in alphabetical order by
    # state, city and venue_name
    # doing a full outer join so that all venues always show
    query = Show.query.join(Venue, full=True).with_entities(
        Venue.city, Venue.state, Venue.name, Venue.id, func.count(Venue.id)
    ).group_by(Venue.city, Venue.state, Venue.name, Venue.id).order_by(Venue.state, Venue.city, Venue.name)

    results = {}

    for city, state, name, id, show_count in query:
        print(city)
        location = (city, state)
        if location not in results:
            results[location] = []
        results[location].append(
            {"id": id, "name": name, "num_upcoming_shows": show_count}
        )

    for (city, state), venues in results.items():
        d = {'city': city, 'state': state, 'venues': venues}
        data.append(d)

    print(data)
    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    # transform form object to dictionary
    search_term = request.form.to_dict(flat=False)['search_term']

    search_term = f"%{search_term}%"

    # note: using .match() is not compatible with SqlLite
    query = Venue.query.filter(Venue.name.match(search_term)).all()

    response = {"count": len(query), "data": query}

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    ct = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    query = Venue.query.get(venue_id)

    if query:
        data = Venue.to_dict(query)

        shows_query = Show.query.join(Venue, full=True).join(Artist).with_entities(
            Venue.id, Venue.name, Show.start_time, Artist.id, Artist.name, Artist.image_link
        ).filter_by(id=venue_id).all()

        upcoming_shows, past_shows, current_show = [], [], {}
        for id, venue, start_time, artist_id, artist_name, artist_image_link in shows_query:
            current_show = {'venue_id': id, 'venue_name': venue, 'artist_id': artist_id, 'artist_name': artist_name,
                            'artist_image_link': artist_image_link, 'start_time': start_time}
            if start_time > ct:
                upcoming_shows.append(current_show)
            else:
                past_shows.append(current_show)

        data.update(
            {
                'upcoming_shows': upcoming_shows,
                'upcoming_shows_count': len(upcoming_shows),
                'past_shows': past_shows,
                'past_shows_count': len(past_shows)
            }
        )

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

    # to_dict(flat=False) returns key: [value] dictionary.
    # Need to flatten the values if array of values has 1 value only.
    data = request.form.to_dict(flat=False)
    try:
        venue = Venue()

        print(data)

        for k, v in data.items():
            # ternary operator that returns v as an array if its key like genres or it has more than 1 value in the list
            setattr(
                venue, 'description' if k == 'seeking_description' else 'website' if 'website' in k else k,
                # ternary operator that joins array into string if the key is genre
                v if k.find('genres') != -1
                # also returns True if value is y and False if it's not y on seeking_venue
                else True if v[0] == 'y' else False if k.find('seeking_talent') != -1
                # alternatively flatten the object if there's only 1 value in the array
                else v[0]
            )
        print(venue.to_dict())

        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success

        flash('Venue "' + venue.name + '" was successfully listed!')
    except Exception as e:
        db.session.rollback()
        # On unsuccessful db insert, flash an error instead.
        flash(f'An error occurred. Venue could not be listed. Error: {e}')
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

    # list all artists alphabetically by their name
    data = Artist.query.order_by(Artist.name).all()

    return render_template('pages/artists.html', artists=data)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    # Implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = f"%{request.form.get('search_term')}%"

    # tried using .match instead of .ilike - ilike is case insensitive and friendlier to wild cards.
    # .match did not return NickiJ when searching nic.
    query = Artist.query.filter(Artist.name.ilike(search_term)).all()

    response = {'count': len(query), 'data': query}
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # Shows the artist page with the given artist_id
    # Replace with real artist data from the artist table, using artist_id
    ct = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    query = Artist.query.get(artist_id)

    if artist_id:
        data = Artist.to_dict(query)

        print(data)

        shows_query = Show.query.join(Venue, full=True).join(Artist, full=True).with_entities(
            Venue.id, Venue.name, Show.start_time, Venue.image_link
        ).filter_by(id=artist_id).all()

        req = dict(('website' if 'website' in k else k, v)
                   for k, v in data.items())

        data = req

        data['genres'] = re.split(',', data['genres'])

        upcoming_shows, past_shows, current_show = [], [], {}
        for id, venue, start_time, venue_image_link in shows_query:
            current_show = {'venue_id': id, 'venue_name': venue,
                            'venue_image_link': venue_image_link, 'start_time': start_time}
            if start_time > ct:
                upcoming_shows.append(current_show)
            else:
                past_shows.append(current_show)

        data.update(
            {
                'upcoming_shows': upcoming_shows,
                'upcoming_shows_count': len(upcoming_shows),
                'past_shows': past_shows,
                'past_shows_count': len(past_shows)
            }
        )

        print(data)

        return render_template('pages/show_artist.html', artist=data)
    return render_template('errors/404.html'), 404

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    query = Artist.query.get(artist_id)

    if query:
        data = Artist.to_dict(query)
        # rename key website to website_link for form
        # (that uses website_link while everything else called it website...)
        req = dict(('website_link' if 'website' in k else k, v)
                   for k, v in data.items())
        for k, v in req.items():
            if k == 'id':
                continue
            form[f'{k}'].data = v

        return render_template('forms/edit_artist.html', form=form, artist=data)
    else:
        print(f'Artist with id {artist_id} could not be found.')
    # Populate form with fields from artist with ID <artist_id>
    return render_template('errors/404.html'), 404


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # Take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    data = Artist.query.filter_by(id=artist_id).first()

    if data:
        if form.validate():
            try:
                # this consistency annoyed me - having website in the template pages as the property field but
                # website_link for the same thing in the forms!! :\
                form_dict = request.form.to_dict(flat=False)

                # rename website_link to website
                req = dict(('website' if 'website' in k else k, v)
                           for k, v in form_dict.items())

                if not hasattr(req.items(), 'seeking_venue'):
                    setattr(data, 'seeking_venue', False)

                print(req.items())

                for k, v in req.items():
                    setattr(
                        data, k,
                        # ternary operator that joins array into string if the key is genre
                        ','.join(v) if k.find('genres') != -1
                        # also returns True if value is y and False if it's not y on seeking_venue
                        else (True if v[0] == 'y' else False) if k.find('seeking_venue') != -1
                        # alternatively flatten the object if there's only 1 value in the array
                        else v[0]
                    )

                print(data)

                db.session.merge(data)
                db.session.commit()
            except Exception as e:
                print(e)

            return redirect(url_for('show_artist', artist_id=artist_id))
        else:
            print(form.errors)

    return render_template('errors/404.html'), 404


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # Populate form with values from venue with ID <venue_id>
    query = Venue.query.get(venue_id)
    if query:
        data = Venue.to_dict(query)
        # rename website to website_link
        req = dict(('website_link' if 'website' in k else k, v)
                   for k, v in data.items())

        for k, v in req.items():
            if k == 'id':
                continue
            if k == 'description':
                form[f'seeking_{k}'].data = v
            else:
                form[f'{k}'].data = v

        print(data)

        return render_template('forms/edit_venue.html', form=form, venue=data)
    else:
        print(f'Venue with id {venue_id} not found.')
    return render_template('errors/404.html'), 404


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form)
    data = Venue.query.filter_by(id=venue_id).first()

    if data:
        if form.validate():
            try:
                form_dict = request.form.to_dict(flat=False)

                # rename website_link to website
                req = dict(('website' if 'website' in k else k, v)
                           for k, v in form_dict.items())

                if not hasattr(req.items(), 'seeking_talent'):
                    print('there is talent being sought!')
                    setattr(data, 'seeking_talent', False)

                for k, v in req.items():
                    setattr(
                        data, k,
                        v if k.find('genres') != -1
                        # handling form truthy/falsy submission
                        else (True if 'y' in v[0] else False) if k.find('seeking_talent') != -1
                        else v[0] if len(v) == 1
                        else v
                    )

                db.session.merge(data)
                db.session.commit()
            except Exception as e:
                print(e)

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
    data = request.form.to_dict(flat=False)
    try:
        artist = Artist()

        for k, v in data.items():
         # ternary operator that returns v as an array if its key like genres or it has more than 1 value in the list
            setattr(
                artist, 'website' if 'website' in k else k,
                # ternary operator that joins array into string if the key is genre
                ','.join(v) if k.find('genres') != -1
                # also returns True if value is y and False if it's not y on seeking_venue
                else True if v[0] == 'y' else False if k.find('seeking_venue') != -1
                # alternatively flatten the object if there's only 1 value in the array
                else v[0]
            )

        db.session.add(artist)
        db.session.commit()

        # on successful db insert, flash success
        flash(f'Artist {artist.name} was successfully listed!')
    except Exception as e:
        flash(
            f'An error occurred. Artist {data.get("name")} could not be listed. Error: {e} '
        )

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # Replace with real venues data.

    # The alternative to using a list and map combination..
    query = Show.query.join(Venue).join(Artist).with_entities(
        Venue.name, Venue.id, Artist.name, Artist.id, Artist.image_link, Show.start_time
    ).order_by(Show.start_time).all()

    results = []

    for (venue_name, venue_id, artist_name, artist_id, artist_image, start_time) in query:
        results.append({
            'venue_id': venue_id,
            'venue_name': venue_name,
            'artist_id': artist_id,
            'artist_name': artist_name,
            'artist_image_link': artist_image,
            'start_time': start_time
        })

    return render_template('pages/shows.html', shows=results)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():

    # called to create new shows in the db, upon submitting new show listing form
    # Insert form data as a new Show record in the db, instead
    data = request.form.to_dict()
    try:
        print(data)

        show = Show()

        print(data.items())
        for k, v in data.items():
            setattr(show, k, v)

        db.session.add(show)
        db.session.commit()

        flash(f'Show successfully booked for {show.start_time}!')

    except Exception as e:
        flash(f'An error occurred. Show could not be listed. Error: {e}')

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
