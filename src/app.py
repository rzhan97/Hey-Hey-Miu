#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2022-01-05
@author: zoe
"""

# !flask/bin/python
from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import pickle
import pandas as pd

# import python module
from prediction import get_top_n_for_user
from client_login import get_user_df

app = Flask(__name__)
Bootstrap(app)

# define the path for model and feature transformer
model_path = "models/final_model.pkl"
loaded_model = pickle.load(open(model_path, 'rb'))
loaded_df = pd.read_pickle("data/processed/userrating_df")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """
    Collect the input and predict the outcome
    Returns:
        Results.html with prediction
    """
    if request.method == 'POST':
        # get input statement
        # namequery = request.form['namequery']
        # data = [namequery]
        # # get the clean data
        # clean_data = process_text(str(data))
        # test_features = loaded_transformer.transform([" ".join(clean_data)])

        client_id = "4c5002e39c9e4d1cabc45d1a8e13101c"
        client_secret = "eb368f429c87478f87aac17554bd64f0"
        user_df = get_user_df(client_id,client_secret,"medium_term")
        my_prediction = get_top_n_for_user(user_df, loaded_df, loaded_model, n=10)

    return render_template('results.html', prediction=my_prediction)


if __name__ == '__main__':
    app.run(debug=True)