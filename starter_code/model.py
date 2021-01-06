#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from app import db
from datetime import datetime
#--------------------------------------------------
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
   #--------------------------New Records----------------------
    website = db.Column(db.String(120)) 
    genres = db.Column(db.ARRAY(db.String(120)))
    seeking_talent = db.Column(db.Boolean,default=False) 
    seeking_description = db.Column(db.String(500))
    venue_artist = db.relationship("Show",backref='venue', lazy='dynamic')
    def __repr__(self):
        return f'<Venue ID: {self.id},name: {self.name}>'
    #------------------------------------------------------------
class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(120)) 
    seeking_venue = db.Column(db.Boolean,default=False) 
    seeking_description = db.Column(db.String(500))
    artist_venue = db.relationship("Show",backref='artist', lazy='dynamic')
    def __repr__(self):
        return f'<Artist ID: {self.id},name: {self.name}>'
    # -----------------------------------------------------
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# ----------------Relationship between Venues and Artists--------------------
class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id =  db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_id  = db.Column( db.Integer,db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f'<Show : Venue ID: {self.venue_id},Artist ID: {self.artist_id}>'
   