from app import app, db
from app.models import Track, Phrase, Playlist

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Track': Track, 'Phrase' : Phrase, 'Playlist' : Playlist}
