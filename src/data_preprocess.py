#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021-12-22
@author: zoe
"""
import requests
import json
import time
import pandas as pd
import numpy as np
from random import sample
import selenium
from tqdm import tqdm
from scipy import sparse
import pickle


# shared secret:5e11e4bca8ad54566e466513df709822
def lastfm_get(payload):
    headers = {'user-agent': 'rzhan97'}
    url = 'http://ws.audioscrobbler.com/2.0/'

    payload['api_key'] = '5e11e4bca8ad54566e466513df709822'
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response


# This function is only help for me to understand json file
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


# This function is helping me get all the users' info

def lookup_userinfo(user):
    response = lastfm_get({
        'method': 'user.getInfo',
        'user': user
    })

    if response.status_code != 200:
        return None

    name = response.json()['user']['realname']
    country = response.json()['user']['country']
    playcount = response.json()['user']['playcount']

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return name, country, playcount


# Build a funtion to get user's top track, I also wrote a function about user's loved song and recent songs
# However, recent songs cannot represent user like it or not, and user usually won't liked a song in Las.fm website
# They tend to link the music app account with last.fm and listen music on their own music app
def lookup_topsong(user):
    response = lastfm_get({
        'method': 'user.getTopTracks',
        'user': user
    })

    if response.status_code != 200:
        return None

    song = [t['name'] for t in response.json()['toptracks']['track']]
    playcount = [t['playcount'] for t in response.json()['toptracks']['track']]
    artist = [t['artist']['name'] for t in response.json()['toptracks']['track']]

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return song, playcount, artist


# Build a funtion to get song's metadata
def lookup_songinfo(track, artist):
    response = lastfm_get({
        'method': 'track.getInfo',
        'track': track,
        'artist': artist
    })

    if response.status_code != 200:
        return None
    try:
        duration = response.json()['track']['duration']
    except:
        duration = None
    try:
        listeners = response.json()['track']['listeners']
    except:
        listeners = None
    try:
        playcount = response.json()['track']['playcount']
    except:
        playcount = None
    try:
        album = response.json()['track']['album']['title']
    except:
        album = None
    try:
        tags = [t['name'] for t in response.json()['track']['toptags']['tag']]
    except:
        tags = None
    try:
        published_date = response.json()['track']['wiki']['published']
    except:
        published_date = None

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return duration, listeners, playcount, album, tags, published_date


def load_user_name(path):
    # Load the user's list again
    with open(path) as f:
        user = json.load(f)
    return user


def get_usersong_df(user):
    # convert them into dataframe, also get the artist with the song, in case there are duplicate song name
    song = []
    artist = []
    count = []
    users = []
    for i in tqdm(range(len(user))):
        data = lookup_topsong(user[i])
        try:
            song.extend(data[0])
            count.extend(data[1])
            artist.extend(data[2])
            users.extend([user[i]] * 50)
        except:
            continue

    usersong_df = pd.DataFrame(zip(users, artist, song, count), columns=['user', 'artist', 'songs', 'count'])

    return usersong_df


def convert_to_userrating(usersong_df):
    # Combine artist and songs together

    usersong_df['song'] = usersong_df["artist"] + "-" + usersong_df["songs"]
    usersong_df = usersong_df.drop(['artist'], axis=1)
    usersong_df = usersong_df.drop(['songs'], axis=1)

    usersong_df[["count"]] = usersong_df[["count"]].apply(pd.to_numeric)

    cols = ['user', 'song', 'count']
    usersong_df = pd.DataFrame(load_df, columns=cols)

    usersong_df['new_rating'] = usersong_df.groupby('user').transform(
        lambda x: ((5 - 1) / ((x.max() + 0.00001) - x.min())) * (x - x.max()) + 5)
    usersong_df = usersong_df.reset_index(drop=True)
    userrating_df = usersong_df

    return userrating_df


def get_user_info(user):
    # Get user's info
    # convert them into dataframe,also get user's infoun
    name = []
    country = []
    playcount = []
    for i in tqdm(range(len(user))):
        data = lookup_userinfo(user[i])
        # use this function to get the
        try:
            name.append(data[0])
            country.append(data[1])
            playcount.append(data[2])
        except:
            continue

    user_df = pd.DataFrame(zip(user, name, country, playcount),
                           columns=['user', 'name', 'country', 'playcount'])

    return user_df

def get_song_info(userrating_df):
    # Get user's info
    # convert them into dataframe,also get user's infoun
    songs_df = pd.DataFrame(userrating_df.song.str.split('-', 1).tolist(),
                            columns=['artist', 'songs'])

    songs_df = songs_df.drop_duplicates()
    songs_list = songs_df.songs.tolist()
    artists_list = songs_df.artist.tolist()

    # Get each song's info for later use
    duration = []
    listeners = []
    playcount = []
    album = []
    tags = []
    published_date = []

    for i in tqdm(range(len(songs_list))):
        data = lookup_songinfo(songs_list[i], artists_list[i])
        # if any records get error
        duration.append(data[0])
        listeners.append(data[1])
        playcount.append(data[2])
        album.append(data[3])
        tags.append(data[4])
        published_date.append(data[5])

    song_df = pd.DataFrame(zip(songs_list, artists_list, duration, listeners, playcount, album, tags, published_date),
                           columns=['song', 'artist', 'duration', 'listeners', 'playcount', 'album', 'tags',
                                    'published_date'])

    return song_df
