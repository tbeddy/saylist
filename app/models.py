from app import db

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    artists = db.Column(db.String(64), nullable=False)
    album = db.Column(db.String(64), nullable=False)
    spot_id = db.Column(db.String(64), unique=True, nullable=False)
    image_url = db.Column(db.String(100), nullable=False)
    phrase = db.relationship('Phrase', backref='track', lazy=True, uselist=False)

    def __repr__(self):
        return "\"{}\" by {} ({})".format(self.name,
                                          self.artists,
                                          self.album)

class Phrase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), index=True, unique=True)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))

    def __repr__(self):
        return "<Phrase {}>".format(self.name)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), index=True, unique=True, nullable=False)
    url_id = db.Column(db.String(32), index=True, unique=True, nullable=False)
    tracks_str = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return "<Playlist {}>".format(self.name)

    def tracks(self):
        track_ids = self.tracks_str.split('-')
        return [Track.query.filter_by(id=int(x)).first()
                for x in track_ids]
