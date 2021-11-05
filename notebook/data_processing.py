#!/usr/bin/env python
# coding: utf-8

# # Data processing

# In[13]:


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


# In[15]:


#load the dataframe that saved and drop all the duplicate in case
load_df = pd.read_pickle("../data/raw/scraped/usersong")
load_df = load_df.drop_duplicates()
load_df.shape[0]


# In[16]:


#Take a look at the loaded dataframe
load_df.head(10)


# In[17]:


#Make sure the count is numeric
load_df[["count"]] = load_df[["count"]].apply(pd.to_numeric)


# In[18]:


#Change the dataframe into a matrix, which will be better to fit in our collaborative filtering algorithm
usersong_matrix_df = load_df.pivot_table(index='user', columns='song', values='count').fillna(0)
usersong_matrix_df.head(10)


# In[20]:


#Also save this matrix dataframe just in case 4.32GB
usersong_matrix_df.to_pickle("../data/processed/usersong_matrix_df")
usersong_matrix_load_df = pd.read_pickle("../data/processed/usersong_matrix_df")


# In[21]:


usersong_matrix_sparse_df = sparse.csr_matrix(usersong_matrix_load_df.values)


# In[22]:


#See the info of this dataframe
usersong_matrix_load_df.info()


# In[23]:


usersong_matrix_df.shape[0]


# # Use matrix to fit into collaborative filtering package surprise

# In[11]:


#How to cite?
# @article{Hug2020,
#   doi = {10.21105/joss.02174},
#   url = {https://doi.org/10.21105/joss.02174},
#   year = {2020},
#   publisher = {The Open Journal},
#   volume = {5},
#   number = {52},
#   pages = {2174},
#   author = {Nicolas Hug},
#   title = {Surprise: A Python library for recommender systems},
#   journal = {Journal of Open Source Software}
# }


# In[15]:


#!pip install scikit-surprise


# In[16]:


import pandas as pd
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from surprise.model_selection import GridSearchCV
from surprise import BaselineOnly
from surprise.model_selection import cross_validate


# # Play around with the dataset

# In[ ]:


def __init__(self, metric, algorithm, k, data, decode_id_song):
  # .
  self.model = self._recommender().fit(data)

def _recommender(self):
  return NearestNeighbors(metric=self.metric, algorithm=self.algorithm, 
                          n_neighbors=self.k, n_jobs=-1)

# Instantiate and fit the model
model = Recommender(metric='cosine', algorithm='brute', k=20, data=mat_songs_features, 
                    decode_id_song=decode_id_song)


# In[ ]:


def _get_recommendations(self, new_song, n_recommendations):
    recom_song_id = self._fuzzy_matching(song=new_song)
    # Return the n neighbors for the song id
    distances, indices = self.model.kneighbors(self.data[recom_song_id], 
                                               n_neighbors=n_recommendations+1)
    return sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), 
                  key=lambda x: x[1])[:0:-1]

def _map_indeces_to_song_title(self, recommendation_ids):
    # get reverse mapper
    return {song_id: song_title for song_title, song_id in self.decode_id_song.items()}


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




