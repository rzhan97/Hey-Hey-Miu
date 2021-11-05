#!/usr/bin/env python
# coding: utf-8

# # Data scraping with Last.fm API

# In[2]:


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


# ### Function used for data scripting

# In[13]:


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


# In[14]:


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


# In[15]:


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


# In[16]:


#Build a funtion to get song's metadata
def lookup_songinfo(track,artist):
    response = lastfm_get({
    'method': 'track.getInfo',
    'track' : track,
    'artist':artist
    })

    if response.status_code != 200:
        return None

    duration = response.json()['track']['duration']
    listeners = response.json()['track']['listeners']
    playcount = response.json()['track']['playcount']
    album = response.json()['track']['album']['title'] 
    tags = [t['name'] for t in response.json()['track']['toptags']['tag'] ]
    try:
        published_date = response.json()['track']['wiki']['published']
    except:
        published_date = None

    # rate limiting
    if not getattr(response, 'from_cache', False):
        time.sleep(0.25)
    return duration,listeners,playcount,album,tags,published_date


# ### Use try/except to catch the failed users

# In[7]:


#Get my neighbors' neighbors' neighbors, which is 3rd connection with me.
#This is the quickiest way to get users' name. However, those are all the users might have similar taste with me.
#To reduce some bias, I will only sample 10,000 users from those users
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from tqdm import tqdm
#def get_users(username):
path = "/Users/zoe/Desktop/chromedriver"
driver = webdriver.Chrome(path)
driver.get("https://www.last.fm/user/rzhan97/neighbours")
user = []
time.sleep(2)
user_names = driver.find_elements_by_class_name("user-list-name")
for i in tqdm(range(len(user_names))):
#    while True:
#        try:
        time.sleep(2)
        user_link = user_names[i].find_element_by_tag_name('a').get_attribute('href')+"/neighbours"
        print(user_link)
        time.sleep(2)
        driver.get(user_link)
        user_names = driver.find_elements_by_class_name("user-list-name")
        for i in range(len(user_names)):
            time.sleep(2)
            user_link = user_names[i].find_element_by_tag_name('a').get_attribute('href')+"/neighbours"
            time.sleep(2)
            driver.get(user_link)
            user_names = driver.find_elements_by_class_name("user-list-name")
            for i in range(len(user_names)):
                user.append(user_names[i].text)
            driver.back()
            time.sleep(2)
            user_names = driver.find_elements_by_class_name("user-list-name")
        driver.back()
        user_names = driver.find_elements_by_class_name("user-list-name")
user = list(dict.fromkeys(user))
driver.quit()
#return user


# In[8]:


#Save the user's list into disk
with open('../data/raw/scraped/user.json', 'w') as f:
    json.dump(user, f)


# In[9]:


#Load the user's list again
with open('../data/raw/scraped/user.json') as f:
    user2 = json.load(f)


# In[10]:


#Check how many users we have
print(len(user2))


# In[11]:


#Filtering 10,000 from the list
rzhan97_small_list= sample(user2,10000)


# In[19]:


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


#Save this dataframe
usersong_rating.to_pickle("../data/raw/scraped/usersong")


# # Get users' info

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
user_df.to_pickle("user_df")


# In[ ]:


user_df.tail()


# In[ ]:


user_df.to_pickle("../data/processed/user_df")


# # Get songs' info

# In[137]:


#Prepare for the song's metadata 
songs_df = usersong_df[['songs', 'artist']] 
songs_df = songs_df.drop_duplicates()
songs_list = songs_df.songs.tolist()
artists_list = songs_df.artist.tolist()
print(len(songs_list))


# ### Question: Do we have another quicker way to do this?

# In[ ]:


#Get each song's info for later use
duration = []
listeners = []
playcount = []
album = []
tags = []
published_date = []

for i in range(len(songs_list)):
    data = lookup_songinfo(songs[i],artists_list[i])
    #if any records get error
    try:
        duration.append(data[0])
        listeners.append(data[1])
        playcount.append(data[2])
        album.append(data[3])
        tags.append(data[4])
        published_date.append(data[5])
    except:
        continue


song_df = pd.DataFrame(zip(songs,artists_list,duration,listeners,playcount,album,tags,published_date), columns =['song','artist','duration','listeners','playcount','album','tags','published_date'])
song_df.to_pickle("song_df")


# In[ ]:





# In[ ]:




