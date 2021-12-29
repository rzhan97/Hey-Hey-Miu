{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "71d92cdd",
   "metadata": {},
   "source": [
    "# Data processing"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 61,
   "id": "33568b29",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "import json\n",
    "import time\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from random import sample\n",
    "import selenium\n",
    "from tqdm import tqdm\n",
    "from scipy import sparse\n",
    "import pickle"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "8e4b31f8",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Load the user's list again\n",
    "with open('../data/raw/scraped/user.json') as f:\n",
    "    user2 = json.load(f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "887ce3c6",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "44246\n"
     ]
    }
   ],
   "source": [
    "#Check how many users we have\n",
    "print(len(user2))"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "569b6c1d",
   "metadata": {},
   "source": [
    "To avoid the bias in those users, I will randomly smaple 10000 users from all the users I have. "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "81f0ac0a",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Filtering 9,999 + 1 from the list\n",
    "rzhan97_small_list= sample(user2,9999)\n",
    "rzhan97_small_list.append('rzhan97')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f341e461",
   "metadata": {},
   "outputs": [],
   "source": [
    "with open('../data/raw/processed/small_list.json', 'w') as f:\n",
    "    json.dump(rzhan97_small_list, f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 77,
   "id": "8986d960",
   "metadata": {},
   "outputs": [],
   "source": [
    "#shared secret:5e11e4bca8ad54566e466513df709822\n",
    "def lastfm_get(payload):\n",
    "\n",
    "    headers = {'user-agent': 'rzhan97'}\n",
    "    url = 'http://ws.audioscrobbler.com/2.0/'\n",
    "\n",
    "    payload['api_key'] = '5e11e4bca8ad54566e466513df709822'\n",
    "    payload['format'] = 'json'\n",
    "\n",
    "    response = requests.get(url, headers=headers, params=payload)\n",
    "    return response\n",
    "\n",
    "#This function is only help for me to understand json file\n",
    "def jprint(obj):\n",
    "    text = json.dumps(obj, sort_keys=True, indent=4)\n",
    "    print(text)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "54916964",
   "metadata": {},
   "outputs": [],
   "source": [
    "#This function is helping me get all the users' info\n",
    "def lookup_userinfo(user):\n",
    "    response = lastfm_get({\n",
    "    'method': 'user.getInfo',\n",
    "    'user' : user\n",
    "    })\n",
    "\n",
    "    if response.status_code != 200:\n",
    "        return None\n",
    "\n",
    "    name = response.json()['user']['realname']\n",
    "    country = response.json()['user']['country']\n",
    "    playcount = response.json()['user']['playcount']\n",
    "\n",
    "\n",
    "    # rate limiting\n",
    "    if not getattr(response, 'from_cache', False):\n",
    "        time.sleep(0.25)\n",
    "    return name,country,playcount"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "id": "78bd97a7",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Build a funtion to get user's top track, I also wrote a function about user's loved song and recent songs\n",
    "#However, recent songs cannot represent user like it or not, and user usually won't liked a song in Las.fm website\n",
    "#They tend to link the music app account with last.fm and listen music on their own music app\n",
    "def lookup_topsong(user):\n",
    "    response = lastfm_get({\n",
    "    'method': 'user.getTopTracks',\n",
    "    'user' : user\n",
    "    })\n",
    "\n",
    "    if response.status_code != 200:\n",
    "        return None\n",
    "\n",
    "    song = [t['name'] for t in response.json()['toptracks']['track']]\n",
    "    playcount = [t['playcount'] for t in response.json()['toptracks']['track']]\n",
    "    artist = [t['artist']['name'] for t in response.json()['toptracks']['track']]\n",
    "\n",
    "\n",
    "    # rate limiting\n",
    "    if not getattr(response, 'from_cache', False):\n",
    "        time.sleep(0.25)\n",
    "    return song,playcount,artist"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "2aec0e6e",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Build a funtion to get song's metadata\n",
    "def lookup_songinfo(track,artist):\n",
    "    response = lastfm_get({\n",
    "    'method': 'track.getInfo',\n",
    "    'track' : track,\n",
    "    'artist':artist\n",
    "    })\n",
    "\n",
    "    if response.status_code != 200:\n",
    "        return None\n",
    "    try:\n",
    "        duration = response.json()['track']['duration']\n",
    "    except:\n",
    "        duration = None\n",
    "    try:\n",
    "        listeners = response.json()['track']['listeners']\n",
    "    except:\n",
    "        listeners = None\n",
    "    try:\n",
    "        playcount = response.json()['track']['playcount']\n",
    "    except:\n",
    "        playcount = None\n",
    "    try:\n",
    "        album = response.json()['track']['album']['title'] \n",
    "    except:\n",
    "        album = None\n",
    "    try:\n",
    "        tags = [t['name'] for t in response.json()['track']['toptags']['tag'] ]\n",
    "    except:\n",
    "        tags = None\n",
    "    try:\n",
    "        published_date = response.json()['track']['wiki']['published']\n",
    "    except:\n",
    "        published_date = None\n",
    "\n",
    "    # rate limiting\n",
    "    if not getattr(response, 'from_cache', False):\n",
    "        time.sleep(0.25)\n",
    "    return duration,listeners,playcount,album,tags,published_date"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "id": "a53b0c2c",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 10000/10000 [2:55:28<00:00,  1.05s/it] \n"
     ]
    }
   ],
   "source": [
    "#convert them into dataframe, also get the artist with the song, in case there are duplicate song name\n",
    "song = []\n",
    "artist = []\n",
    "count = []\n",
    "user = []\n",
    "for i in tqdm(range(len(rzhan97_small_list))):\n",
    "    data = lookup_topsong(rzhan97_small_list[i])\n",
    "    try:\n",
    "        song.extend(data[0])\n",
    "        count.extend(data[1])\n",
    "        artist.extend(data[2])\n",
    "        user.extend([rzhan97_small_list[i]]*50)\n",
    "    except:\n",
    "        continue\n",
    "\n",
    "\n",
    "usersong_df = pd.DataFrame(zip(user,artist,song,count), columns =['user','artist','songs','count'])\n"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "6d47a985",
   "metadata": {},
   "source": [
    "Take a look at how this dataframe looks like"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "917aa59d",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>artist</th>\n",
       "      <th>songs</th>\n",
       "      <th>count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Ollie MN</td>\n",
       "      <td>Please Never Fall in Love Again</td>\n",
       "      <td>98</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish</td>\n",
       "      <td>Your Power</td>\n",
       "      <td>76</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>My Chemical Romance</td>\n",
       "      <td>Teenagers</td>\n",
       "      <td>74</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish</td>\n",
       "      <td>Lost Cause</td>\n",
       "      <td>71</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Black Box Recorder</td>\n",
       "      <td>Child Psychology</td>\n",
       "      <td>67</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         user               artist                            songs count\n",
       "0  iheartpiss             Ollie MN  Please Never Fall in Love Again    98\n",
       "1  iheartpiss        Billie Eilish                       Your Power    76\n",
       "2  iheartpiss  My Chemical Romance                        Teenagers    74\n",
       "3  iheartpiss        Billie Eilish                       Lost Cause    71\n",
       "4  iheartpiss   Black Box Recorder                 Child Psychology    67"
      ]
     },
     "execution_count": 15,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Take a look at this dataframe\n",
    "usersong_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "id": "7443cb27",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Change to another dataframe\n",
    "usersong_rating = usersong_df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "308e365f",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>count</th>\n",
       "      <th>song</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>98</td>\n",
       "      <td>Ollie MN-Please Never Fall in Love Again</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>76</td>\n",
       "      <td>Billie Eilish-Your Power</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>74</td>\n",
       "      <td>My Chemical Romance-Teenagers</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>71</td>\n",
       "      <td>Billie Eilish-Lost Cause</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>67</td>\n",
       "      <td>Black Box Recorder-Child Psychology</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>64</td>\n",
       "      <td>Mitski-I Bet on Losing Dogs</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>54</td>\n",
       "      <td>Misty Miller-Happy Together</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>54</td>\n",
       "      <td>The Beatles-Eleanor Rigby - Remastered 2009</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>51</td>\n",
       "      <td>Billie Eilish-my future</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>51</td>\n",
       "      <td>girl in red-Serotonin</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         user count                                         song\n",
       "0  iheartpiss    98     Ollie MN-Please Never Fall in Love Again\n",
       "1  iheartpiss    76                     Billie Eilish-Your Power\n",
       "2  iheartpiss    74                My Chemical Romance-Teenagers\n",
       "3  iheartpiss    71                     Billie Eilish-Lost Cause\n",
       "4  iheartpiss    67          Black Box Recorder-Child Psychology\n",
       "5  iheartpiss    64                  Mitski-I Bet on Losing Dogs\n",
       "6  iheartpiss    54                  Misty Miller-Happy Together\n",
       "7  iheartpiss    54  The Beatles-Eleanor Rigby - Remastered 2009\n",
       "8  iheartpiss    51                      Billie Eilish-my future\n",
       "9  iheartpiss    51                        girl in red-Serotonin"
      ]
     },
     "execution_count": 17,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Combine artist and songs together\n",
    "usersong_rating['song'] = usersong_rating[\"artist\"] + \"-\" + usersong_rating[\"songs\"]\n",
    "usersong_rating = usersong_rating.drop(['artist'], axis=1)\n",
    "usersong_rating = usersong_rating.drop(['songs'], axis=1)\n",
    "usersong_rating.head(10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "554dc8f7",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "<class 'pandas.core.frame.DataFrame'>\n",
      "RangeIndex: 498444 entries, 0 to 498443\n",
      "Data columns (total 3 columns):\n",
      " #   Column  Non-Null Count   Dtype \n",
      "---  ------  --------------   ----- \n",
      " 0   user    498444 non-null  object\n",
      " 1   count   498444 non-null  object\n",
      " 2   song    498444 non-null  object\n",
      "dtypes: object(3)\n",
      "memory usage: 11.4+ MB\n"
     ]
    }
   ],
   "source": [
    "usersong_rating.info()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "aaf23ccc",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Save this dataframe\n",
    "usersong_rating.to_pickle(\"../data/processed/usersong\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "e8f9c46d",
   "metadata": {},
   "source": [
    "# Get users' info"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "id": "b6015ab9",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 10000/10000 [1:59:22<00:00,  1.40it/s] \n"
     ]
    }
   ],
   "source": [
    "#Get user's info\n",
    "#convert them into dataframe,also get user's infoun\n",
    "name = []\n",
    "country = []\n",
    "playcount = []\n",
    "for i in tqdm(range(len(rzhan97_small_list))):\n",
    "    data = lookup_userinfo(rzhan97_small_list[i])\n",
    "    #use this function to get the \n",
    "    try:\n",
    "        name.append(data[0])\n",
    "        country.append(data[1])\n",
    "        playcount.append(data[2])\n",
    "    except:\n",
    "        continue\n",
    "\n",
    "\n",
    "user_df = pd.DataFrame(zip(rzhan97_small_list,name,country,playcount), columns =['user','name','country','playcount'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "id": "d6e749b0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>name</th>\n",
       "      <th>country</th>\n",
       "      <th>playcount</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>9995</th>\n",
       "      <td>holynoodles</td>\n",
       "      <td></td>\n",
       "      <td>None</td>\n",
       "      <td>2937</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9996</th>\n",
       "      <td>hao97zone</td>\n",
       "      <td></td>\n",
       "      <td>None</td>\n",
       "      <td>1188</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9997</th>\n",
       "      <td>monse2312</td>\n",
       "      <td>mo</td>\n",
       "      <td>United States</td>\n",
       "      <td>1133</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9998</th>\n",
       "      <td>defohr96</td>\n",
       "      <td>fortunaa</td>\n",
       "      <td>Indonesia</td>\n",
       "      <td>26572</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9999</th>\n",
       "      <td>rzhan97</td>\n",
       "      <td></td>\n",
       "      <td>None</td>\n",
       "      <td>3553</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "             user      name        country playcount\n",
       "9995  holynoodles                     None      2937\n",
       "9996    hao97zone                     None      1188\n",
       "9997    monse2312        mo  United States      1133\n",
       "9998     defohr96  fortunaa      Indonesia     26572\n",
       "9999      rzhan97                     None      3553"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "user_df.tail()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "id": "ba29cbee",
   "metadata": {},
   "outputs": [],
   "source": [
    "user_df.to_pickle(\"../data/processed/user_df\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "f8bcb8de",
   "metadata": {},
   "source": [
    "# Get songs' info"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "id": "006a5415",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "with open('../data/processed/usersong', 'rb') as f:\n",
    "    usersong_df = pickle.load(f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "id": "5a5e5fd6",
   "metadata": {},
   "outputs": [],
   "source": [
    "songs_df = pd.DataFrame(usersong_df.song.str.split('-',1).tolist(),\n",
    "                                 columns = ['artist','songs'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "id": "8c03b8c0",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>artist</th>\n",
       "      <th>songs</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>Ollie MN</td>\n",
       "      <td>Please Never Fall in Love Again</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Billie Eilish</td>\n",
       "      <td>Your Power</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>My Chemical Romance</td>\n",
       "      <td>Teenagers</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>Billie Eilish</td>\n",
       "      <td>Lost Cause</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Black Box Recorder</td>\n",
       "      <td>Child Psychology</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                artist                            songs\n",
       "0             Ollie MN  Please Never Fall in Love Again\n",
       "1        Billie Eilish                       Your Power\n",
       "2  My Chemical Romance                        Teenagers\n",
       "3        Billie Eilish                       Lost Cause\n",
       "4   Black Box Recorder                 Child Psychology"
      ]
     },
     "execution_count": 19,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "songs_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "id": "daa1f439",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "89636\n"
     ]
    }
   ],
   "source": [
    "#Prepare for the song's metadata \n",
    "songs_df = songs_df.drop_duplicates()\n",
    "songs_list = songs_df.songs.tolist()\n",
    "artists_list = songs_df.artist.tolist()\n",
    "print(len(songs_list))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 91,
   "id": "a3bdfd10",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 89636/89636 [10:02:35<00:00,  2.48it/s]  \n"
     ]
    }
   ],
   "source": [
    "#Get each song's info for later use\n",
    "duration = []\n",
    "listeners = []\n",
    "playcount = []\n",
    "album = []\n",
    "tags = []\n",
    "published_date = []\n",
    "\n",
    "for i in tqdm(range(len(songs_list))):\n",
    "    data = lookup_songinfo(songs_list[i],artists_list[i])\n",
    "    #if any records get error\n",
    "    duration.append(data[0])\n",
    "    listeners.append(data[1])\n",
    "    playcount.append(data[2])\n",
    "    album.append(data[3])\n",
    "    tags.append(data[4])\n",
    "    published_date.append(data[5])\n",
    "\n",
    "\n",
    "song_df = pd.DataFrame(zip(songs_list,artists_list,duration,listeners,playcount,album,tags,published_date), columns =['song','artist','duration','listeners','playcount','album','tags','published_date'])\n",
    "song_df.to_pickle(\"../data/processed/song_df\")"
   ]
  },
  {
   "cell_type": "markdown",
   "id": "533e367d",
   "metadata": {},
   "source": [
    "# To make user rating dataframe fit our suprise package"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "id": "2ffd31aa",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "498444"
      ]
     },
     "execution_count": 26,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "load_df = pd.read_pickle(\"../data/processed/usersong\")\n",
    "load_df.shape[0]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "id": "aed484cf",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>count</th>\n",
       "      <th>song</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>98</td>\n",
       "      <td>Ollie MN-Please Never Fall in Love Again</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>76</td>\n",
       "      <td>Billie Eilish-Your Power</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>74</td>\n",
       "      <td>My Chemical Romance-Teenagers</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>71</td>\n",
       "      <td>Billie Eilish-Lost Cause</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>67</td>\n",
       "      <td>Black Box Recorder-Child Psychology</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>64</td>\n",
       "      <td>Mitski-I Bet on Losing Dogs</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>54</td>\n",
       "      <td>Misty Miller-Happy Together</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>54</td>\n",
       "      <td>The Beatles-Eleanor Rigby - Remastered 2009</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>51</td>\n",
       "      <td>Billie Eilish-my future</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>9</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>51</td>\n",
       "      <td>girl in red-Serotonin</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         user count                                         song\n",
       "0  iheartpiss    98     Ollie MN-Please Never Fall in Love Again\n",
       "1  iheartpiss    76                     Billie Eilish-Your Power\n",
       "2  iheartpiss    74                My Chemical Romance-Teenagers\n",
       "3  iheartpiss    71                     Billie Eilish-Lost Cause\n",
       "4  iheartpiss    67          Black Box Recorder-Child Psychology\n",
       "5  iheartpiss    64                  Mitski-I Bet on Losing Dogs\n",
       "6  iheartpiss    54                  Misty Miller-Happy Together\n",
       "7  iheartpiss    54  The Beatles-Eleanor Rigby - Remastered 2009\n",
       "8  iheartpiss    51                      Billie Eilish-my future\n",
       "9  iheartpiss    51                        girl in red-Serotonin"
      ]
     },
     "execution_count": 27,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Take a look at the loaded dataframe\n",
    "load_df.head(10)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "id": "2628324a",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Make sure the count is numeric\n",
    "load_df[[\"count\"]] = load_df[[\"count\"]].apply(pd.to_numeric)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "id": "48da8c2b",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>song</th>\n",
       "      <th>count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Ollie MN-Please Never Fall in Love Again</td>\n",
       "      <td>98</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish-Your Power</td>\n",
       "      <td>76</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>My Chemical Romance-Teenagers</td>\n",
       "      <td>74</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish-Lost Cause</td>\n",
       "      <td>71</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Black Box Recorder-Child Psychology</td>\n",
       "      <td>67</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         user                                      song  count\n",
       "0  iheartpiss  Ollie MN-Please Never Fall in Love Again     98\n",
       "1  iheartpiss                  Billie Eilish-Your Power     76\n",
       "2  iheartpiss             My Chemical Romance-Teenagers     74\n",
       "3  iheartpiss                  Billie Eilish-Lost Cause     71\n",
       "4  iheartpiss       Black Box Recorder-Child Psychology     67"
      ]
     },
     "execution_count": 53,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Changed the column name here to fit more data\n",
    "cols = ['user', 'song', 'count']\n",
    "load_df = pd.DataFrame(load_df, columns = cols)\n",
    "load_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "id": "bbbd0dc6",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Changed the column name here to fit more data\n",
    "cols = ['user', 'song', 'count']\n",
    "load_df = pd.DataFrame(load_df, columns = cols)\n",
    "#Nomalize our count for each user\n",
    "#As I realized, I cannot assigned 1 as the lowest rating, since user usually give 3 if they listen several times, which means they actually mildly like it\n",
    "#Maximum add 0.00001 to avoid dividing by 0's error\n",
    "load_df['new_rating'] = load_df.groupby('user').transform(lambda x: ((5-1)/((x.max()+0.00001)-x.min())) * (x - x.max())+5)\n",
    "load_df = load_df.reset_index(drop=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "id": "d89df593",
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>user</th>\n",
       "      <th>song</th>\n",
       "      <th>count</th>\n",
       "      <th>new_rating</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Ollie MN-Please Never Fall in Love Again</td>\n",
       "      <td>98</td>\n",
       "      <td>5.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish-Your Power</td>\n",
       "      <td>76</td>\n",
       "      <td>3.686567</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>My Chemical Romance-Teenagers</td>\n",
       "      <td>74</td>\n",
       "      <td>3.567164</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Billie Eilish-Lost Cause</td>\n",
       "      <td>71</td>\n",
       "      <td>3.388060</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>iheartpiss</td>\n",
       "      <td>Black Box Recorder-Child Psychology</td>\n",
       "      <td>67</td>\n",
       "      <td>3.149254</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "         user                                      song  count  new_rating\n",
       "0  iheartpiss  Ollie MN-Please Never Fall in Love Again     98    5.000000\n",
       "1  iheartpiss                  Billie Eilish-Your Power     76    3.686567\n",
       "2  iheartpiss             My Chemical Romance-Teenagers     74    3.567164\n",
       "3  iheartpiss                  Billie Eilish-Lost Cause     71    3.388060\n",
       "4  iheartpiss       Black Box Recorder-Child Psychology     67    3.149254"
      ]
     },
     "execution_count": 75,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#Take a look at the current data\n",
    "load_df.head()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "id": "a6f1b4f1",
   "metadata": {},
   "outputs": [],
   "source": [
    "#Save my dataframe\n",
    "load_df.to_pickle(\"../data/processed/userrating_df\")"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.8"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
