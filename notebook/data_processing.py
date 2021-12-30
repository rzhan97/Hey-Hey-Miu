#!/usr/bin/env python
# coding: utf-8

# # Data processing

# In[7]:


import requests
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from random import sample
import selenium
from tqdm import tqdm
from scipy import sparse
import pickle


# In[8]:


#Load the user's list again
with open('../data/raw/scraped/user.json') as f:
    user2 = json.load(f)


# In[4]:


#Check how many users we have
print(len(user2))


# To avoid the bias in those users, I will randomly smaple 10000 users from all the users I have. 

# In[10]:


#Filtering 9,999 + 1 from the list
rzhan97_small_list= sample(user2,9999)
rzhan97_small_list.append('rzhan97')


# In[12]:


with open('../data/processed/small_list.json', 'w') as f:
    json.dump(rzhan97_small_list, f)


# In[2]:


#shared secret:5e11e4bca8ad54566e466513df709822
def lastfm_get(payload):

    headers = {'user-agent': 'rzhan97'}
    url = 'http://ws.audioscrobbler.com/2.0/'

    payload['api_key'] = '5e11e4bca8ad54566e466513df709822'
    payload['format'] = 'json'

    response = requests.get(url, headers=headers, params=payload)
    return response

#This function is only help for me to understand json file
def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


# In[3]:


#This function is helping me get all the users' info
def lookup_userinfo(user):
    response = lastfm_get({
    'method': 'user.getInfo',
    'user' : user
    })

    if response.status_code != 200:
        return None

    name = response.json()['user']['realname']
    country = response.json()['user']['country']
    playcount = response.json()['user']['playcount']


    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return name,country,playcount


# In[4]:


#Build a funtion to get user's top track, I also wrote a function about user's loved song and recent songs
#However, recent songs cannot represent user like it or not, and user usually won't liked a song in Las.fm website
#They tend to link the music app account with last.fm and listen music on their own music app
def lookup_topsong(user):
    response = lastfm_get({
    'method': 'user.getTopTracks',
    'user' : user
    })

    if response.status_code != 200:
        return None

    song = [t['name'] for t in response.json()['toptracks']['track']]
    playcount = [t['playcount'] for t in response.json()['toptracks']['track']]
    artist = [t['artist']['name'] for t in response.json()['toptracks']['track']]


    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return song,playcount,artist


# In[5]:


#Build a funtion to get song's metadata
def lookup_songinfo(track,artist):
    response = lastfm_get({
    'method': 'track.getInfo',
    'track' : track,
    'artist':artist
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
        tags = [t['name'] for t in response.json()['track']['toptags']['tag'] ]
    except:
        tags = None
    try:
        published_date = response.json()['track']['wiki']['published']
    except:
        published_date = None

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return duration,listeners,playcount,album,tags,published_date


# In[17]:


#convert them into dataframe, also get the artist with the song, in case there are duplicate song name
song = []
artist = []
count = []
user = []
for i in tqdm(range(len(rzhan97_small_list))):
    data = lookup_topsong(rzhan97_small_list[i])
    try:
        song.extend(data[0])
        count.extend(data[1])
        artist.extend(data[2])
        user.extend([rzhan97_small_list[i]]*50)
    except:
        continue


usersong_df = pd.DataFrame(zip(user,artist,song,count), columns =['user','artist','songs','count'])


# Take a look at how this dataframe looks like

# In[20]:


#Take a look at this dataframe
usersong_df.head()


# In[21]:


#Change to another dataframe
usersong_rating = usersong_df


# In[22]:


#Combine artist and songs together
usersong_rating['song'] = usersong_rating["artist"] + "-" + usersong_rating["songs"]
usersong_rating = usersong_rating.drop(['artist'], axis=1)
usersong_rating = usersong_rating.drop(['songs'], axis=1)
usersong_rating.head(10)


# In[23]:


usersong_rating.info()


# In[24]:


#Save this dataframe
usersong_rating.to_pickle("../data/processed/usersong")


# In[8]:


import pandas as pd
load_df = pd.read_pickle("../data/processed/usersong")


# In[9]:


load_df.tail()


# # Get users' info

# In[17]:


rzhan97_small_list = load_df['user'].unique()


# In[18]:


#Get user's info
#convert them into dataframe,also get user's infoun
name = []
country = []
playcount = []
for i in tqdm(range(len(rzhan97_small_list))):
    data = lookup_userinfo(rzhan97_small_list[i])
    #use this function to get the 
    try:
        name.append(data[0])
        country.append(data[1])
        playcount.append(data[2])
    except:
        continue


user_df = pd.DataFrame(zip(rzhan97_small_list,name,country,playcount), columns =['user','name','country','playcount'])


# In[19]:


user_df.tail()


# In[20]:


user_df.to_pickle("../data/processed/user_df")


# # Get songs' info

# In[30]:


with open('../data/processed/usersong', 'rb') as f:
    usersong_df = pickle.load(f)


# In[31]:


songs_df = pd.DataFrame(usersong_df.song.str.split('-',1).tolist(),
                                 columns = ['artist','songs'])


# In[32]:


songs_df.head()


# In[33]:


#Prepare for the song's metadata 
songs_df = songs_df.drop_duplicates()
songs_list = songs_df.songs.tolist()
artists_list = songs_df.artist.tolist()
print(len(songs_list))


# In[ ]:


#Get each song's info for later use
duration = []
listeners = []
playcount = []
album = []
tags = []
published_date = []

for i in tqdm(range(len(songs_list))):
    data = lookup_songinfo(songs_list[i],artists_list[i])
    #if any records get error
    duration.append(data[0])
    listeners.append(data[1])
    playcount.append(data[2])
    album.append(data[3])
    tags.append(data[4])
    published_date.append(data[5])


song_df = pd.DataFrame(zip(songs_list,artists_list,duration,listeners,playcount,album,tags,published_date), columns =['song','artist','duration','listeners','playcount','album','tags','published_date'])
song_df.to_pickle("../data/processed/song_df")


# # To make user rating dataframe fit our suprise package

# In[23]:


load_df = pd.read_pickle("../data/processed/usersong").drop_duplicates()
load_df.shape[0]


# In[24]:


#Take a look at the loaded dataframe
load_df.head(10)


# In[25]:


#Make sure the count is numeric
load_df[["count"]] = load_df[["count"]].apply(pd.to_numeric)


# In[26]:


#Changed the column name here to fit more data
cols = ['user', 'song', 'count']
load_df = pd.DataFrame(load_df, columns = cols)
load_df.head()


# In[27]:


#Nomalize our count for each user
#As I realized, I cannot assigned 1 as the lowest rating, since user usually give 3 if they listen several times, which means they actually mildly like it
#Maximum add 0.00001 to avoid dividing by 0's error
load_df['new_rating'] = load_df.groupby('user').transform(lambda x: ((5-1)/((x.max()+0.00001)-x.min())) * (x - x.max())+5)
load_df = load_df.reset_index(drop=True)


# In[28]:


#Take a look at the current data
load_df.head()


# In[29]:


#Save my dataframe
load_df.to_pickle("../data/processed/userrating_df")


# # Try a new user

# In[ ]:


#Get user's info
#convert them into dataframe,also get user's infoun
name = []
country = []
playcount = []
for i in tqdm(range(len(rzhan97_small_list))):
    data = lookup_userinfo(rzhan97_small_list[i])
    #use this function to get the 
    try:
        name.append(data[0])
        country.append(data[1])
        playcount.append(data[2])
    except:
        continue


user_df = pd.DataFrame(zip(rzhan97_small_list,name,country,playcount), columns =['user','name','country','playcount'])


# In[ ]:


load_df[load_df.user == "Kany1314"]


# In[10]:


lookup_topsong("Kany1314")


# In[14]:


data = lookup_topsong("Kany1314")
song =[]
count = []
artist = []
user = []
song.extend(data[0])
count.extend(data[1])
artist.extend(data[2])
user.extend(["Kany1314"]*50)


Kany1314_df = pd.DataFrame(zip(user,artist,song,count), columns =['user','artist','songs','count'])


# In[15]:


Kany1314_df.head()


# In[16]:


#Combine artist and songs together
Kany1314_df['song'] = Kany1314_df["artist"] + "-" + Kany1314_df["songs"]
Kany1314_df = Kany1314_df.drop(['artist'], axis=1)
Kany1314_df = Kany1314_df.drop(['songs'], axis=1)
Kany1314_df.head(10)


# In[18]:


#Make sure the count is numeric
Kany1314_df[["count"]] = Kany1314_df[["count"]].apply(pd.to_numeric)
#Changed the column name here to fit more data
cols = ['user', 'song', 'count']
Kany1314_df = pd.DataFrame(Kany1314_df, columns = cols)
Kany1314_df.head()


# In[20]:


#Nomalize our count for each user
#As I realized, I cannot assigned 1 as the lowest rating, since user usually give 3 if they listen several times, which means they actually mildly like it
#Maximum add 0.00001 to avoid dividing by 0's error
Kany1314_df['new_rating'] = Kany1314_df.groupby('user').transform(lambda x: ((5-1)/((x.max()+0.00001)-x.min())) * (x - x.max())+5)
Kany1314_df = Kany1314_df.reset_index(drop=True)


# In[21]:


#Take a look at the current data
Kany1314_df.head()


# In[22]:


#Save my dataframe
Kany1314_df.to_pickle("../data/processed/new_user_df")


# In[ ]:




