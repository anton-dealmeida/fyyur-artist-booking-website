from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

db = SQLAlchemy()


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
