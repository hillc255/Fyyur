from datetime import datetime
from flask_wtf import Form
from wtforms import BooleanField, StringField, SelectField, SelectMultipleField, DateTimeField, ValidationError
from wtforms.validators import ValidationError, DataRequired, AnyOf, URL, Regexp, Optional
import re

def seeking(Form, seeking_venue):
  if seeking_venue == 'seeking_venue':
        seeking_venue = True
  else:
        seeking_venue = False
  return seeking_venue


genres_choices = [
    ('Alternative', 'Alternative'),
    ('Blues', 'Blues'),
    ('Classical', 'Classical'),
    ('Country', 'Country'),
    ('Electronic', 'Electronic'),
    ('Folk', 'Folk'),
    ('Funk', 'Funk'),
    ('Hip-Hop', 'Hip-Hop'),
    ('Heavy Metal', 'Heavy Metal'),
    ('Instrumental', 'Instrumental'),
    ('Jazz', 'Jazz'),
    ('Musical Theatre', 'Musical Theatre'),
    ('Pop', 'Pop'),
    ('Punk', 'Punk'),
    ('R&B', 'R&B'),
    ('Reggae', 'Reggae'),
    ('Rock n Roll', 'Rock n Roll'),
    ('Soul', 'Soul'),
    ('Other', 'Other'),
]
state_choices = [
    ('AK', 'AK'),
    ('AL', 'AL'),
    ('AR', 'AR'),
    ('AZ', 'AZ'),
    ('CA', 'CA'),
    ('CO', 'CO'),
    ('CT', 'CT'),
    ('DC', 'DC'),
    ('DE', 'DE'),
    ('FL', 'FL'),
    ('GA', 'GA'),
    ('HI', 'HI'),
    ('IA', 'IA'),
    ('ID', 'ID'),
    ('IL', 'IL'),
    ('IN', 'IN'),
    ('KS', 'KS'),
    ('KY', 'KY'),
    ('LA', 'LA'),
    ('MA', 'MA'),
    ('MD', 'MD'),
    ('ME', 'ME'),
    ('MI', 'MI'),
    ('MN', 'MN'),
    ('MO', 'MO'),
    ('MS', 'MS'),
    ('MT', 'MT'),
    ('NC', 'NC'),
    ('ND', 'ND'),
    ('NE', 'NE'),
    ('NH', 'NH'),
    ('NJ', 'NJ'),
    ('NM', 'NM'),
    ('NV', 'NV'),
    ('NY', 'NY'),
    ('OH', 'OH'),
    ('OK', 'OK'),
    ('OR', 'OR'),
    ('PA', 'PA'),
    ('RI', 'RI'),
    ('SC', 'SC'),
    ('SD', 'SD'),
    ('TN', 'TN'),
    ('TX', 'TX'),
    ('UT', 'UT'),
    ('VA', 'VA'),
    ('VT', 'VT'),
    ('WA', 'WA'),
    ('WI', 'WI'),
    ('WV', 'WV'),
    ('WY', 'WY'),
]


class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
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
        choices=state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), Regexp(r'^[2-9]\d{2}-\d{3}-\d{4}$', message=': Invalid phone number.')]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],       
        choices=genres_choices
    )
    facebook_link = StringField(
        'facebook_link', validators=[DataRequired(), URL(message=': Invalid URL.')]
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
        choices=state_choices
    )
    phone = StringField(
        # TODO implement validation logic
        'phone', validators=[DataRequired(), Regexp(r'^[2-9]\d{2}-\d{3}-\d{4}$', message=': Invalid phone number.')]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(message=': Invalid URL.')]
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[DataRequired()],
        choices=genres_choices
    )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[Optional(), URL(message=': Invalid URL.')]
    )
    website = StringField(
        'website', validators=[Optional(), URL(message=': Invalid URL.')]
    )
    seeking_venue = BooleanField(
        'seeking_venue', validators=[DataRequired()]
    )


# TODO IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM
