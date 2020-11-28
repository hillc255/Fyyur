#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import logging
import sys
from datetime import datetime
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Flask, Response, abort, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from sqlalchemy import Column, Date, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text
from sqlalchemy.dialects import postgresql as pg

from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venues'
   
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  genres = db.Column(pg.ARRAY(db.String, dimensions=1), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  website = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean,default=True)
  seeking_description = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  artists = db.relationship('Artist', secondary='shows')
  shows = db.relationship('Show', backref=('venues'))

    # TODO: implement any missing fields, as a database migration 
    # using Flask-Migrate
    
class Artist(db.Model):
  __tablename__ = 'artists'
    
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  genres = db.Column(pg.ARRAY(db.String, dimensions=1), nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120), nullable=False)
  facebook_link = db.Column(db.String(500))
  website = db.Column(db.String(500))
  seeking_venue = db.Column(db.Boolean,default=True)
  seeking_description = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  venues = db.relationship('Venue', secondary='shows', cascade='all', 

lazy='dynamic')
  shows = db.relationship('Show', backref=('artists'))

# TODO: implement any missing fields, as a database migration using Flask-

Migrate

# TODO Implement Show and Artist models, and complete all model...database migration.

class Show(db.Model):
  __tablename__ = 'shows'
    
  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, ForeignKey('venues.id'),  nullable=False)
  artist_id = db.Column(db.Integer, ForeignKey('artists.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)
  upcoming_shows = db.Column(db.Boolean,default=True)
  venue = db.relationship('Venue')
  artist = db.relationship('Artist')

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

# TypeError thown - jinga seems dedundant if decorator exists
@app.template_filter('datetime')
def format_datetime(value, format):
#def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

#app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  ----------------------------------------------------------------
#  Venues

 # TODO: replace with real venues data.

@app.route('/venues')
def venues():
  
  citystate_areas = db.session.query(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for area in citystate_areas:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []

    for venue in area_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
         "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
     })
  
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": venue_data
    })

  return render_template('pages/venues.html', areas=data)

#  ----------------------------------------------------------------

# TODO: implement search on venues with partial string search.
# Ensure it is case-insensitive.

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  search_results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()

  data = []
  
  for result in search_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": len(search_results),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))  

# TODO: replace with real venue data from the venues table, using venue_id
# shows the venue page with the given venue_id

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.get(venue_id)

  upcoming_show = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
  past_show = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).all()
  
  upcoming_shows = []
  past_shows = []

  for show in upcoming_show:
    upcoming_shows.append({
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      }) 
    past_shows_count = len(upcoming_show) 

  for show in past_show:
    past_shows.append({
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      }) 
    past_shows_count = len(past_show) 

  data = {  
    "name": venue.name,
    "id": venue.id,
    "genres": venue.genres,
    "city": venue.city,
    "address": venue.address,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows
  }
    
  return render_template('pages/show_venue.html', venue=data)    

#  ----------------------------------------------------------------
#  Create Venue

# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  if form.validate_on_submit():
    try:
      venue = Venue()
      form.populate_obj(venue)
      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except ValueError as e:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred in ' + form.name + '. Error: ' + str(e))
    finally:
      db.session.close()

  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ':, '.join(errors))
    flash(f'Errors: {message}')

  return render_template('pages/home.html')

# TODO: Complete this endpoint for taking a venue_id, and using
# SQLAlchemy ORM to delete a record. 
# Handle cases where the session commit could fail.

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):

  error = False
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()

  except:
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  if error: 
    flash('An error occurred. Venue could not be deleted.')
  if not error: 
    flash('Venue was successfully deleted!')
  
  return redirect(url_for('index'))

#  ----------------------------------------------------------------
#  Artists

# TODO: implement search on artists with partial string search.
# Ensure it is case-insensitive.

@app.route('/artists')
def artists():

  data = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@property
def artist_list(self):
  return { 'id': self.id, 'name': self.name }

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  search_results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  data = []
  
  for result in search_results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": len(search_results),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))  

# Shows the artist page with the given venue_id
# TODO: replace with real venue data from the venues table, using venue_id

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  global data

  artist = Artist.query.get(artist_id)

  #query to get shows by venue
  upcoming_show = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()
  past_show = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).all()

  #define empty list for shows
  upcoming_shows = []
  past_shows = []

  #loop for upcoming and past shows
  for show in upcoming_show:
    upcoming_shows.append({
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      }) 
    past_shows_count = len(upcoming_show) 

  for show in past_show:
    past_shows.append({
        'start_time': show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
      }) 
    past_shows_count = len(past_show) 
  
  data = {  
    "name": artist.name,
    "id": artist.id,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "upcoming_shows": upcoming_shows,
    "past_shows": past_shows
  }
  
  return render_template('pages/show_artist.html', artist=data) 

#  ----------------------------------------------------------------
#  Update (This is not required?)

# TODO: populate form with fields from artist with ID <artist_id>

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
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
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

# TODO: take values from the form submitted, and update existing
# artist record with ID <artist_id> using the new attributes

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  return redirect(url_for('show_artist', artist_id=artist_id))

# TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
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

  return render_template('forms/edit_venue.html', form=form, venue=venue)

# TODO: take values from the form submitted, and update existing
# venue record with ID <venue_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Create Artist

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

# TODO: insert form data as a new Venue record in the db, instead
# TODO: modify data to be the data object returned from db insertion
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      artist = Artist()
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

    except ValueError as e:
      print(sys.exc_info())
      db.session.rollback()
      flash('An error occurred in ' + form.name + '. Error: ' + str(e))
    finally:
      db.session.close()

  else:
    message = []
    for field, errors in form.errors.items():
      message.append(field + ':, '.join(errors))
    flash(f'Errors: {message}')

  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Shows

# displays list of shows at /shows
# TODO: replace with real venues data.
# num_shows should be aggregated based on number of upcoming shows per venue.

@app.route('/shows')
def shows():

  shows_query = db.session.query(Show).join(Artist).join(Venue).all()

  data = []
  for show in shows_query: 
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/search', methods=['POST'])
def search_shows():

  search_term = request.form.get('search_term', '')
  search_results = db.session.query(Show).join(Artist).join(Venue).filter(Show.start_time).ilike(f'%{search_term}%').all()
 
  #search_results = db.session.query(Show).join(Artist).join(Venue).filter(Show.start_time.ilike(f'%{search_term}%')).all()

  data = []
  
  for result in search_results:
    data.append({
      "venue_id": result.venue_id,
      "venue_name": result.venue.name,
      "artist_id": result.artist_id,
      "artist_name": result.artist.name, 
      "artist_image_link": result.artist.image_link,
      "start_time": str(result.start_time)
    })

  response={
    "data": data
  }
  return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', '')) 

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

# called to create new shows in the db, upon submitting new show listing form
# TODO: insert form data as a new Show record in the db, instead
# on successful db insert, flash success
# TODO: on unsuccessful db insert, flash an error instead.
#create new show with form

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  error = False

  try: 
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']

    shows = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    
    db.session.add(shows)
    db.session.commit()
  except: 
    error = True
    print(sys.exc_info())
    db.session.rollback()
  finally: 
    db.session.close()
  if error: 
    flash('An error occurred. Show could not be listed.')
  if not error: 
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
    app.run(host='127.0.0.1', port=port)
'''
