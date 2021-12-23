#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021-12-22
@author: zoe zhang
"""

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_user_name(root_user,path):
    """
    Function use to scrap all the user we need

    :param root_user: the root user's id
    :param path: webdriver located, current path  = "/Users/zoe/Desktop/chromedriver"
    :return: a list of all the users
    """
    driver = webdriver.Chrome(path)
    driver.get("https://www.last.fm/user/"+root_user+"/neighbours")
    user = []
    first_user = []
    second_user = []
    # My neighbors,1st connection
    user_names = driver.find_elements(By.CLASS_NAME, "user-list-name")

    for i in range(len(user_names)):
        first_user.append(user_names[i].text)

    for i in range(len(first_user)):
        user_link = "https://www.last.fm/user/" + first_user[i] + "/neighbours"
        driver.get(user_link)
        # My neighbors' neighbors, 2nd connection
        user_name2 = driver.find_elements(By.CLASS_NAME, "user-list-name")
        for i in range(len(user_name2)):
            second_user.append(user_name2[i].text)

    # Get rid of the duplicate user
    second_user = list(dict.fromkeys(second_user))

    third_user = []
    for i in range(len(second_user)):
        user_link = "https://www.last.fm/user/" + second_user[i] + "/neighbours"
        driver.get(user_link)
        # My neighbors' neighbors, 2nd connection
        user_name3 = driver.find_elements(By.CLASS_NAME, "user-list-name")
        for i in range(len(user_name3)):
            third_user.append(user_name3[i].text)

    # Get rid of the duplicate user
    third_user = list(dict.fromkeys(third_user))
    user = list(dict.fromkeys(third_user))

    return user

