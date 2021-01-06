#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort,flash
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------
from flask_migrate import Migrate
from sqlalchemy.orm import  relationship, backref
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.sql import label


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migratedb = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from model import *
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. 
  location_query =db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  result = []
  for venues in location_query:
       location_result = Venue.query.filter(Venue.state == venues.state).filter(Venue.city == venues.city).all()
       
       located_venues = [{
                'id': venue.id,
                'name': venue.name,
               
                   }for venue in location_result ]
       result.append({
                'city': venues.city,
                'state': venues.state,
                'venues': located_venues,
                
            })
  
  return render_template('pages/venues.html', areas=result)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_value = request.form.get('search_term', '')
  term = "%{}%".format(search_value)
  resualt = Venue.query.filter(Venue.name.ilike(term)).all()
  response ={
    "count": len(resualt),
    "data": resualt
}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  active_venues = Venue.query.get(venue_id)
  q = db.session.query(Venue).join(Show, Venue.id==Show.venue_id).filter(Show.start_time>datetime.now()).all()
  # TODO: replace with real venue data from the venues table, using venue_id
  real_data = {
    "id": active_venues.id,
    "name": active_venues.name,
    "genres": active_venues.genres,
    "address": active_venues.address,
    "city": active_venues.city,
    "state": active_venues.state,
    "phone": active_venues.phone,
    "facebook_link": active_venues.facebook_link,
    "website": active_venues.website,
    "image_link": active_venues.image_link,
     'upcoming_shows':len(q),
  }

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=real_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
  error = False  
  try:
     venue = Venue(
      name=request.form.get("name"),
      city=request.form.get("city"),
      state=request.form.get("state"),
      address=request.form.get("address"),
      phone=request.form.get("phone"),
      facebook_link=request.form.get("facebook_link"),
      genres=request.form.getlist('genres'),
      website=request.form.get("website"),
      image_link=request.form.get("image_link"))
     db.session.add(venue)
     db.session.commit()
       # on successful db insert, flash success
     flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except():
     db.session.rollback()
     error = True
     # TODO: on unsuccessful db insert, flash an error instead.
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
     db.session.close()
     # References:https://stackoverflow.com/questions/42579079/flask-post-data-to-table-using-sqlalchemy-mysql
     #https://www.codementor.io/@garethdwyer/building-a-crud-application-with-flask-and-sqlalchemy-dm3wv7yu2
#------------------------------------------------------------------------------------------#


  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        delete_venues =Venue.query.get(venue_id)
        db.session.delete(delete_venues)
        db.session.commit()
        flash('Venue was successfully Deleted!')
    except():
        db.session.rollback()
        error = True
        flash('An error occurred. Venue could not be Deleted.')
    finally:
        db.session.close()

    return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_query = Artist.query.all()
  artist_result = [
            {
               "id":artist.id,
              "name":artist.name,
              
            } for artist in artist_query]

  return render_template('pages/artists.html', artists=artist_result)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_value = request.form.get('search_term', '')
  term = "%{}%".format(search_value)
  resualt = Artist.query.filter(Artist.name.ilike(term)).all()
  response ={
    "count": len(resualt),
    "data": resualt
            }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  active_artists = Artist.query.get(artist_id)
  real_data = {
    "id": active_artists.id,
    "name": active_artists.name,
    "genres": active_artists.genres,
    "city": active_artists.city,
    "state": active_artists.state,
    "phone": active_artists.phone,
    "facebook_link": active_artists.facebook_link,
    "website": active_artists.website,
    "image_link": active_artists.image_link,
    
  }
 
 # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=real_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  edit_artists = Artist.query.get(artist_id)

  form = ArtistForm(
    name = edit_artists.name,
    city = edit_artists.city,
    state = edit_artists.state,
    phone = edit_artists.phone,
    genres = edit_artists.genres,
    facebook_link = edit_artists.facebook_link,
    image_link=edit_artists.image_link,
    website=edit_artists.website
  )

  return render_template('forms/edit_artist.html', form=form, artist=edit_artists)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error=False
  update = Artist.query.get(artist_id)
  try:
     update.name = request.form.get("name")
     update.city = request.form.get("city")
     update.state = request.form.get("state")
     update.phone = request.form.get("phone")
     update.genres = request.form.getlist("genres")
     update.facebook_link = request.form.get("facebook_link")
     update.website= request.form.get("website")
     update.image_link=request.form.get("image_link")
     db.session.commit()
     flash('Artist ' + request.form['name'] + ' was successfully Updated!')
  except():
     db.session.rollback()
     error = True
     flash('An error occurred. Artist ' + request.form['name'] + 'could not be Updated.')
  finally:
     db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()   
  # TODO: replace with real venue data from the venues table, using venue_id
  edit_venues = Venue.query.get(venue_id)
  form = VenueForm(
    name = edit_venues.name,
    city = edit_venues.city,
    state = edit_venues.state,
    phone = edit_venues.phone,
    address = edit_venues.address,
    genres = edit_venues.genres,
    facebook_link = edit_venues.facebook_link,
    website= edit_venues.website,
    image_link=edit_venues.image_link
  )
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=edit_venues)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error=False
  update = Venue.query.get(venue_id)
  try:
     update.name = request.form.get("name")
     update.city = request.form.get("city")
     update.state = request.form.get("state")
     update.address = request.form.get("address")
     update.phone = request.form.get("phone")
     update.genres = request.form.getlist("genres")
     update.facebook_link = request.form.get("facebook_link")
     update.website=request.form.get("website"),
     update.image_link=request.form.get("image_link"),
     db.session.commit()
     flash('Venue ' + request.form['name'] + ' was successfully Updated!')
  except():
     db.session.rollback()
     error = True
     flash('An error occurred. Venue ' + request.form['name'] + 'could not be Updated.')
  finally:
     db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False   
  try:
     artist = Artist(name=request.form.get("name"),
      city=request.form.get("city"),
      state=request.form.get("state"),
      phone=request.form.get("phone"),
      facebook_link=request.form.get("facebook_link"),
      genres=request.form.getlist('genres'),
      image_link=request.form.get("image_link"),
      website=request.form.get("website"),)
     db.session.add(artist)
     db.session.commit()
       # on successful db insert, flash success
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except():
     db.session.rollback()
     error = True
     # TODO: on unsuccessful db insert, flash an error instead.
     # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
     db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

 show_query = db.session.query(Show).join(Artist, Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).all()
 show_query_result = [
            {
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "start_time": str(show.start_time)
            
            } for show in  show_query ]
 
 return render_template('pages/shows.html', shows=show_query_result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False   
  try:
     show = Show(venue_id=request.form.get("venue_id"),
      artist_id=request.form.get("artist_id"),
      start_time=request.form.get("start_time"))

     db.session.add(show)
     db.session.commit()
       # on successful db insert, flash success
     flash('Show was successfully listed!')
  except():
     db.session.rollback()
     error = True
     # TODO: on unsuccessful db insert, flash an error instead.
     # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
     flash('An error occurred. Show could not be listed.')
  finally:
     db.session.close()
  
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
    app.run(host='0.0.0.0', port=port)
'''
