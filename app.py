#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from dataclasses import asdict
from flask_migrate import Migrate, upgrade
from forms import *
from logging import Formatter, FileHandler
import logging
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
import re
import dateutil.parser
import babel
from flask import (Flask, render_template, request,
                   flash, redirect, url_for)

from models import db, Artist, Venue, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app=app)

# Connect to a local postgresql database
# This is done in the config.py and imported on above using app.config.from_object('config')
# This will import settings I define there, this is a best practice for python
migrate = Migrate(app, db)


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

    # used for form validation to ensure the form submitted is valid.
    form = VenueForm(request.form, meta={"csrf": False})

    # to_dict(flat=False) returns key: [value] dictionary.
    # Need to flatten the values if array of values has 1 value only.

    if form.validate():
        try:
            venue = Venue()

            form.populate_obj(venue)

            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success

            flash('Venue "' + venue.name +
                  '" was successfully listed!')

        except Exception as e:
            db.session.rollback()
            # On unsuccessful db insert, flash an error instead.
            flash(
                f'An error occurred. Venue could not be listed. Error: {e}')
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

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

        shows_query = Show.query.filter_by(artist_id=artist_id).join(Venue, full=True).join(Artist, full=True).with_entities(
            Venue.id, Venue.name, Show.start_time, Venue.image_link
        ).all()

        print(shows_query)

        req = dict(('website' if 'website' in k else k, v)
                   for k, v in data.items())

        data = req

        # genres have been reverted to an array of strings.
        # data['genres'] = re.split(',', data['genres'])

        upcoming_shows, past_shows, current_show = [], [], {}

        for id, venue, start_time, venue_image_link in shows_query:
            current_show = {'venue_id': id, 'venue_name': venue,
                            'venue_image_link': venue_image_link, 'start_time': start_time}
            print(current_show)
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
    form = ArtistForm(request.form, meta={'csrf': False})

    data = Artist.query.filter_by(id=artist_id).first()

    if data:
        if form.validate():
            try:
                artist = Artist()
                artist = data
                form.populate_obj(artist)

                db.session.merge(artist)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
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

        for k, v in data.items():
            if k == 'id':
                continue
            if k == 'description':
                form[f'seeking_{k}'].data = v
            else:
                form[f'{k}'].data = v

        return render_template('forms/edit_venue.html', form=form, venue=data)
    else:
        print(f'Venue with id {venue_id} not found.')
    return render_template('errors/404.html'), 404


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # Take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = VenueForm(request.form, meta={'csrf': False})
    data = Venue.query.filter_by(id=venue_id).first()

    if data:
        if form.validate():
            try:
                venue = Venue()
                venue = data
                form.populate_obj(venue)

                db.session.merge(venue)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
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
    # data = request.form.to_dict(flat=False)

    # unpack request.form into ArtistForm object for validation and error handling
    form = ArtistForm(request.form, meta={"csrf": False})

    if form.validate():
        try:
            artist = Artist()

            print(form.data)

            form.populate_obj(artist)

            db.session.add(artist)
            db.session.commit()

            # on successful db insert, flash success
            flash(f'Artist {artist.name} was successfully listed!')
        except Exception as e:
            db.session.rollback()
            flash(
                f'An error occurred. Artist {form.name.data} could not be listed. Error: {e} '
            )
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

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
    form = ShowForm(request.form, meta={"csrf": False})
    if form.validate():
        try:
            show = Show()
            form.populate_obj(show)

            db.session.add(show)
            db.session.commit()

            flash(f'Show successfully booked for {show.start_time}!')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred. Show could not be listed. Error: {e} ')

        return render_template('pages/home.html')
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))


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
