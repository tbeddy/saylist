from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import MemeForm
from app.models import Playlist
from app.play import retrieve_playlist

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = MemeForm()
    if form.validate_on_submit():
        if form.max_length.data:
            track_max = form.max_length.data
        else:
            track_max = len(form.sentence.data.split())

        top_playlist = retrieve_playlist(form.sentence.data, track_max)

        if top_playlist:
            return redirect(url_for('playlist', playlist_id=top_playlist.url_id))
        else:
            flash("A playlist could not be constructed from your input.")
            return redirect(url_for('index'))
    else:
        return render_template('index.html', form=form)

@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    playlist = Playlist.query.filter_by(url_id=playlist_id).first_or_404()
    return render_template('playlist.html', playlist=playlist)
