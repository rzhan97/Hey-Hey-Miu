#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-01-05
@author: zoe
"""

# !flask/bin/python
from flask import Flask, redirect, url_for, request, render_template
from prediction import get_top_n_for_user
import pandas as pd
import pickle
#import pickle
original_df = pd.read_pickle("../data/processed/userrating_df")
original_model = pickle.load(open("../model/final_model.pkl", 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predictions',methods = ['POST', 'GET'])
def predictions():
    # if request.method == 'POST':
    user = request.form['username']
    number_of_recs = int(request.form['number-of-recs'])
    predictions = get_top_n_for_user(user,original_df,original_model,number_of_recs)
    predict_list = predictions.song.tolist()
    print(predict_list)
    return render_template('predict.html',predictions = predict_list)
    # else:
    #     return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True, port=5000)

