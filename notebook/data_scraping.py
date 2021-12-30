#!/usr/bin/env python
# coding: utf-8

# # Data scraping 

# In[1]:


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


# I used to use a nested for loop to catch my 3rd connection, but I found this approach is not effecient enough as there will be duplicate data occuer and will trigger Stale Element Reference Exception error when time is out for store selenium item. To solve this, I sperate them and prepare three list to store them as string to avoid memory issue.

# In[30]:


#Get my neighbors' neighbors' neighbors, which is 3rd connection with me.
#This is the quickiest way to get users' name. However, those are all the users might have similar taste with me.
#To reduce some bias, I will only sample 10,000 users from those users
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# wait = WebDriverWait(driver, 10)
# element = wait.until(EC.element_to_be_clickable((By.ID, 'someid')))

#Try function to avoid error "stale element reference: element is not attached to the page document"
#def get_users(username):
path = "/Users/zoe/Desktop/chromedriver"
driver = webdriver.Chrome(path)
driver.get("https://www.last.fm/user/rzhan97/neighbours")
user = []
first_user = []
second_user = []
#My neighbors,1st connection
user_names = driver.find_elements(By.CLASS_NAME, "user-list-name")
for i in range(len(user_names)):
    first_user.append(user_names[i].text)
    
for i in tqdm(range(len(first_user))):
    user_link = "https://www.last.fm/user/"+first_user[i]+"/neighbours"
    driver.get(user_link)
    #My neighbors' neighbors, 2nd connection
    user_name2 = driver.find_elements(By.CLASS_NAME,"user-list-name")
    for i in range(len(user_name2)):
        second_user.append(user_name2[i].text)

#Get rid of the duplicate user
second_user = list(dict.fromkeys(second_user))
print(len(second_user))


# In[32]:


third_user = []
for i in tqdm(range(len(second_user))):
    user_link = "https://www.last.fm/user/"+second_user[i]+"/neighbours"
    driver.get(user_link)
    #My neighbors' neighbors, 2nd connection
    user_name3 = driver.find_elements(By.CLASS_NAME,"user-list-name")
    for i in range(len(user_name3)):
        third_user.append(user_name3[i].text)
        
#Get rid of the duplicate user
third_user = list(dict.fromkeys(third_user))
print(len(third_user))


# In[33]:


user = list(dict.fromkeys(third_user))


# Save my list

# In[35]:


#Save the user's list into disk
with open('../data/raw/scraped/user.json', 'w') as f:
    json.dump(user, f)


# In[ ]:





# In[ ]:




