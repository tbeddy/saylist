from itertools import combinations, filterfalse
from uuid import uuid4
import sys
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from sqlalchemy import func
from app import app, db
from app.models import Track, Phrase, Playlist

spotify_id = app.config['SPOTIPY_CLIENT_ID']
spotify_secret = app.config['SPOTIPY_CLIENT_SECRET']
spotify_uri = app.config['SPOTIPY_REDIRECT_URI']
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_id,
                                                      client_secret=spotify_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def matching_track(phrase):
    # phrase may not be in the db at all, or it may be a Track-less Phrase
    p = Phrase.query.filter_by(name=phrase).first()
    if not p:
        p = Phrase(name=phrase)
        db.session.add(p)
        db.session.commit()

    form_str = "\'"+phrase+"\'"
    chunk_max = 10
    for chunk in range(chunk_max):
        results = sp.search(q=form_str, type='track', limit=50, offset=chunk*50)
        results = results['tracks']['items']
        for track in results:
            if phrase == track['name'].lower():
                t = Track(name=track['name'],
                          artists=track['artists'][0]['name'],
                          album=track['album']['name'],
                          spot_id=track['id'],
                          image_url=track['album']['images'][0]['url'],
                          phrase=p)
                db.session.add(t)
                db.session.commit()
                return t

def add_playlist_to_db(sentence, pl_tracks):
    pls = [str(track.id) for track in pl_tracks]
    ids_str = "-".join(pls)
    pl = Playlist(name=sentence.lower(),
                  url_id=str(uuid4()).replace('-', ''),
                  tracks_str=ids_str)
    db.session.add(pl)
    db.session.commit()
    return pl

def retrieve_playlist(sentence, max_phrase_length):
    # TODO: Don't let this bypass max_phrase_length
    pl = Playlist.query.filter_by(name=sentence.lower()).first()
    if pl:
        return pl
    
    wordlist = sentence.lower().split()
    splitrange = list(range(1, len(wordlist)))

    # Every possible set of positions to split the sentence
    splits_coll = []
    for i in range(1, len(wordlist)):
        splits_coll += list(combinations(splitrange,i))

    # Every possible subdivision of the sentence (begin with the sentence itself)
    sublist_coll = [[wordlist]]

    for splits in splits_coll:
        a = splits[0]
        z = splits[-1]
        sublist = [wordlist[:a]]
        if (len(splits) == 2):
            sublist.append(wordlist[a:z])
        elif (len(splits) > 2):
            for i,j in zip(splits[:-1], splits[1:]):
                sublist.append(wordlist[i:j])
        sublist.append(wordlist[z:])
        sublist_coll.append(sublist)

    # Remove all sublists with phrases longer than the max_phrase_length
    sublist_coll = list(filter((lambda x: not [i for i in x if len(i) > max_phrase_length]),
                               sublist_coll))

    # Turn each phrase into a string from a list of strings
    sublist_coll = [[" ".join(list(p)) for p in sl] for sl in sublist_coll]

    # Every possible phrase
    phrase_coll = list(set([phrase for sublist in sublist_coll for phrase in sublist]))

    # Search every phrase in the db
    db_phrases = {}
    trackless_phrases = []
    for phrase in phrase_coll:
        maybe_phrase = Phrase.query.filter_by(name=phrase).first()
        if maybe_phrase:
            if maybe_phrase.track:
                db_phrases[phrase] = maybe_phrase.track
            else:
                trackless_phrases.append(phrase)

    # Remove all sublists with (previously searched) trackless phrases
    sublist_coll = list(filter((lambda x: all([i not in trackless_phrases for i in x])),
                               sublist_coll))

    # Return a sublist if all of its phrases have a corresponding track
    for sublist in sublist_coll:
        if all([phrase in db_phrases for phrase in sublist]):
            tracks = [db_phrases[phrase] for phrase in sublist]
            pl = add_playlist_to_db(sentence, tracks)
            return pl

    while(sublist_coll):
        # Sort the sublists by the fewest phrases not in the db
        sublist_coll = sorted(sublist_coll,
                              key=(lambda x: len(list(
                                  filterfalse((lambda y: y in db_phrases), x)))))
        sublist = sublist_coll[0]
        missing_phrases = list(set(filterfalse((lambda y: y in db_phrases), sublist)))
        success_count = 0
        for phrase in missing_phrases:
            maybe_track = matching_track(phrase)
            if maybe_track:
                db_phrases[phrase] = maybe_track
                success_count+=1
        if len(missing_phrases) == success_count:
            tracks = [db_phrases[phrase] for phrase in sublist]
            pl = add_playlist_to_db(sentence, tracks)
            return pl
        else:
            del sublist_coll[0]
