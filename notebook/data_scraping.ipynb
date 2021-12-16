{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Data scraping "
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
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
    "from tqdm import tqdm\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "I used to use a nested for loop to catch my 3rd connection, but I found this approach is not effecient enough as there will be duplicate data occuer and will trigger Stale Element Reference Exception error when time is out for store selenium item. To solve this, I sperate them and prepare three list to store them as string to avoid memory issue."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 50/50 [02:36<00:00,  3.14s/it]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "2046\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "#Get my neighbors' neighbors' neighbors, which is 3rd connection with me.\n",
    "#This is the quickiest way to get users' name. However, those are all the users might have similar taste with me.\n",
    "#To reduce some bias, I will only sample 10,000 users from those users\n",
    "from selenium import webdriver\n",
    "from selenium.webdriver.common.action_chains import ActionChains\n",
    "import time\n",
    "from tqdm import tqdm\n",
    "from selenium.webdriver.common.by import By\n",
    "from selenium.webdriver.support import expected_conditions as EC\n",
    "\n",
    "# wait = WebDriverWait(driver, 10)\n",
    "# element = wait.until(EC.element_to_be_clickable((By.ID, 'someid')))\n",
    "\n",
    "#Try function to avoid error \"stale element reference: element is not attached to the page document\"\n",
    "#def get_users(username):\n",
    "path = \"/Users/zoe/Desktop/chromedriver\"\n",
    "driver = webdriver.Chrome(path)\n",
    "driver.get(\"https://www.last.fm/user/rzhan97/neighbours\")\n",
    "user = []\n",
    "first_user = []\n",
    "second_user = []\n",
    "#My neighbors,1st connection\n",
    "user_names = driver.find_elements(By.CLASS_NAME, \"user-list-name\")\n",
    "for i in range(len(user_names)):\n",
    "    first_user.append(user_names[i].text)\n",
    "    \n",
    "for i in tqdm(range(len(first_user))):\n",
    "    user_link = \"https://www.last.fm/user/\"+first_user[i]+\"/neighbours\"\n",
    "    driver.get(user_link)\n",
    "    #My neighbors' neighbors, 2nd connection\n",
    "    user_name2 = driver.find_elements(By.CLASS_NAME,\"user-list-name\")\n",
    "    for i in range(len(user_name2)):\n",
    "        second_user.append(user_name2[i].text)\n",
    "\n",
    "#Get rid of the duplicate user\n",
    "second_user = list(dict.fromkeys(second_user))\n",
    "print(len(second_user))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 2046/2046 [1:38:42<00:00,  2.89s/it]  "
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "44246\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "third_user = []\n",
    "for i in tqdm(range(len(second_user))):\n",
    "    user_link = \"https://www.last.fm/user/\"+second_user[i]+\"/neighbours\"\n",
    "    driver.get(user_link)\n",
    "    #My neighbors' neighbors, 2nd connection\n",
    "    user_name3 = driver.find_elements(By.CLASS_NAME,\"user-list-name\")\n",
    "    for i in range(len(user_name3)):\n",
    "        third_user.append(user_name3[i].text)\n",
    "        \n",
    "#Get rid of the duplicate user\n",
    "third_user = list(dict.fromkeys(third_user))\n",
    "print(len(third_user))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "user = list(dict.fromkeys(third_user))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Save my list"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Save the user's list into disk\n",
    "with open('../data/raw/scraped/user.json', 'w') as f:\n",
    "    json.dump(user, f)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
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
 "nbformat_minor": 2
}
