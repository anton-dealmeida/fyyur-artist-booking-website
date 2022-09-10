from datetime import datetime
import re
from xml.dom import ValidationErr
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
from enums import Genres, State

states = State.choices()
genres = Genres.choices()

# Custom Validators


def validate_genres(form, field):
    genres_values = [genre[1] for genre in genres]
    for value in field.data:
        if value not in genres_values:
            raise ValidationErr('Invalid genre value.')


def validate_phone(form, field):
    if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
        raise ValidationErr("Invalid phone number.")


def validate_facebook_link(form, field):
    if not 'facebook.com' in field.data:
        raise ValidationErr("Not a valid facebook link.")


class ShowForm(Form):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=states
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # Implement enum restriction
        'genres', validators=[DataRequired(), validate_genres],
        choices=genres
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL(), validate_facebook_link]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField('seeking_talent')

    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=states
    )
    phone = StringField(
        # Implement validation logic for state
        'phone', validators=[validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=genres
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        # removed these validators completely, facebook_link input isn't rendering for some reason.
        # NOTE - removing html input id facebook_link reveals the hidden input...
        'facebook_link', validators=[URL(), validate_facebook_link]
    )

    website_link = StringField(
        'website_link'
    )

    seeking_venue = BooleanField('seeking_venue')

    seeking_description = StringField(
        'seeking_description'
    )
