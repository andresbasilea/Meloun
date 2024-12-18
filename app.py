import os
import json
from flask import Flask, redirect, request, session, url_for, render_template
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

# Load configuration from config.json
with open('config.json') as f:
    config = json.load(f)

CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
REDIRECT_URI = config['redirect_uri']
SCOPE = 'user-library-read user-top-read playlist-read-private streaming'

# Configure app and Spotify authentication
app = Flask(__name__)
app.secret_key = os.urandom(24)

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session['token_info'] = token_info
    print(token_info)
    return redirect(url_for('explore'))

@app.route('/explore')
def explore():
    token_info = session.get('token_info')
    if not token_info:
        return redirect('/')
    
    sp = Spotify(auth=token_info['access_token'])
    results = sp.current_user_playlists()
    playlists = results['items']
    user_id = sp.current_user()['id']

    user_playlists = []
    for playlist in playlists:
        if playlist['owner']['id'] == user_id:
            if playlist['images']:
                playlist_data = {
                    'name': playlist['name'],
                    'image_url': playlist['images'][0]['url'],
                    'first_track_preview_url': None
                }
                # Get the first track's preview URL
                tracks = sp.playlist_tracks(playlist['id'])
                if tracks['items']:
                    first_track = tracks['items'][0]['track']
                    #print(first_track)
                    playlist_data['first_track_preview_url'] = first_track['preview_url']
                    print(playlist_data['first_track_preview_url'])
                user_playlists.append(playlist_data)


    return render_template('explore.html', playlists=user_playlists)

if __name__ == '__main__':
    app.run(debug=True)
    