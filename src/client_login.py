#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-01-05
@author: zoe
"""

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
import numpy as np
import pickle
from surprise import Dataset
from surprise import Reader

client_id = "4c5002e39c9e4d1cabc45d1a8e13101c"
client_secret = "eb368f429c87478f87aac17554bd64f0"

def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame['items']:
        track_ids.append(song['id'])
    return track_ids

def get_track_features(id):
    meta = sp.track(id)
     # meta
    name = meta['name']
    album = meta['album']['name']
    artist = meta['album']['artists'][0]['name']
    spotify_url = meta['external_urls']['spotify']
    album_cover = meta['album']['images'][0]['url']
    track_info = [name, album, artist, spotify_url, album_cover]
    return track_info

def get_user_df(client_id,client_secret,time_range):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                                   redirect_uri="http://127.0.0.1:9090", scope="user-top-read"))

    results = sp.current_user_top_tracks()

    # long_term (calculated from several years of data and including all new data as it becomes available),
    # medium_term (approximately last 6 months),
    # short_term (approximately last 4 weeks). Default: medium_term
    top_tracks_50 = sp.current_user_top_tracks(limit=50, offset=0, time_range=time_range)
    track_ids = get_track_ids(top_tracks_50)

    tracks = []
    for i in range(len(track_ids)):
        time.sleep(.5)
        track = get_track_features(track_ids[i])
        tracks.append(track)
    # create dataset
    df = pd.DataFrame(tracks, columns=['name', 'album', 'artist', 'spotify_url', 'album_cover'])

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,
                                                   redirect_uri="http://127.0.0.1:9090", scope="user-read-private"))
    results = sp.current_user()

    new_user_id = results['id']

    song = df.name
    artist = df.artist
    x = np.linspace(5, 1, num=50)
    y = np.log2(list(range(2, 52)))
    rating = ((x/y)[1:]+1).tolist().insert(0,(x/y)[0])
    user = [new_user_id] * 50
    new_user_df = pd.DataFrame(zip(user, artist + "-" + song, rating), columns=['user', 'song', 'new_rating'])

    return new_user_df