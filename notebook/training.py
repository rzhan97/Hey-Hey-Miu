#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!pip install numpy
#!pip install scikit-surprise


# In[2]:


import pandas as pd
import pickle


# # Load dataset

# In[3]:


load_df = pd.read_pickle("../data/processed/userrating_df")
load_df.shape[0]


# In[10]:


#Create the surprise dataset
from surprise import Dataset
from surprise import Reader
reader = Reader()
data = Dataset.load_from_df(load_df[['user', 'song', 'new_rating']], reader)


# # Check different algorithm

# In[4]:


#Benchmark by using different algorithm
benchmark = []
from surprise import SVD
from surprise import SVDpp
from surprise import NMF
from surprise import NormalPredictor
from surprise import KNNBaseline
from surprise import KNNBasic
from surprise import KNNWithMeans
from surprise import KNNWithZScore
from surprise import BaselineOnly
from surprise import CoClustering
from surprise.model_selection import cross_validate

# Iterate over all algorithms
for algorithm in [SVD(), SVDpp(), NMF(), NormalPredictor(), KNNBaseline(), KNNBasic(), KNNWithMeans(), KNNWithZScore(), BaselineOnly(), CoClustering()]:
    # Perform cross validation
    results = cross_validate(algorithm, data, measures=['RMSE'], cv=3, verbose=False)
    
    # Get results & append algorithm name
    tmp = pd.DataFrame.from_dict(results).mean(axis=0)
    tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
    benchmark.append(tmp)
    
pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')    


# # Choose SVD and the best parameter

# In[14]:


#From the benchmark above, with the low RMSE and fit time, SVD win the game
from surprise import SVD
from surprise.model_selection import GridSearchCV


param_grid = {'n_epochs': [10,20], 'lr_all': [0.002, 0.005, 0.1],
              'reg_all': [0.1, 0.5]}
gs = GridSearchCV(SVD, param_grid, measures=['rmse', 'mae'], cv=3)

gs.fit(data)

# best RMSE score
print(gs.best_score['rmse'])

# combination of parameters that gave the best RMSE score
print(gs.best_params['rmse'])

algo = gs.best_estimator['rmse']


# In[11]:


trainset = data.build_full_trainset()
load_model.fit(trainset)
#algo.fit(data.build_full_trainset())


# In[12]:


load_model.fit(trainset)


# In[8]:


# model_path="../model/final_model.pkl"
# pickle.dump(algo,open(model_path, 'wb'))


# In[15]:


model_path="../model/final_model.pkl"
load_model = pickle.load(open(model_path, 'rb'))


# In[16]:


rzhan97_unknown_song = load_df[load_df.user != "rzhan97"]
rzhan97_unknown_song_list = list(dict.fromkeys(rzhan97_unknown_song.song.tolist())) 
pred_list = []
for song in rzhan97_unknown_song_list:
    pred_list.append(load_model.predict("rzhan97",song, verbose=True))


# # Check the top 10 songs for myself

# In[32]:


rzhan97_df = pd.DataFrame(pred_list, columns=['user', 'song', 'real_rating','est_rating','was_imporsible'])
rzhan97_df.sort_values(by = ['est_rating'], ascending = False).head(10)


# # Evaluation on testset

# In[43]:


from surprise.model_selection import train_test_split, GridSearchCV
#Divide dataset into train and test dataset
trainset, testset = train_test_split(data, test_size=0.25)
predictions = load_model.test(testset)
# algo = gs.best_estimator['rmse']
# predictions = algo.fit(trainset).test(testset)


# In[44]:


from surprise import accuracy
accuracy.rmse(predictions)


# # Try a new user

# In[35]:


Kany1314_df = pd.read_pickle("../data/processed/new_user_df")
Kany1314_df.head()


# In[37]:


load_df.append(Kany1314_df, ignore_index=True)


# In[38]:


Kany1314_unknown_song = load_df[load_df.user != "Kany1314"]
Kany1314_unknown_song_list = list(dict.fromkeys(Kany1314_unknown_song.song.tolist())) 
pred_list = []
for song in Kany1314_unknown_song_list:
    pred_list.append(load_model.predict("Kany1314",song, verbose=True))


# In[39]:


Kany1314_pre_df = pd.DataFrame(pred_list, columns=['user', 'song', 'real_rating','est_rating','was_imporsible'])
Kany1314_pre_df.sort_values(by = ['est_rating'], ascending = False).head(10)


# In[40]:


data = Dataset.load_from_df(load_df[['user', 'song', 'new_rating']], reader)
trainset = data.build_full_trainset()
load_model.fit(trainset)


# In[41]:


Kany1314_unknown_song = load_df[load_df.user != "Kany1314"]
Kany1314_unknown_song_list = list(dict.fromkeys(Kany1314_unknown_song.song.tolist())) 
pred_list = []
for song in Kany1314_unknown_song_list:
    pred_list.append(load_model.predict("Kany1314",song, verbose=True))


# In[42]:


Kany1314_pre_df = pd.DataFrame(pred_list, columns=['user', 'song', 'real_rating','est_rating','was_imporsible'])
Kany1314_pre_df.sort_values(by = ['est_rating'], ascending = False).head(10)


# In[ ]:




