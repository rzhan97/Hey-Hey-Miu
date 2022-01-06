#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021-12-30
@author: zoe
"""
from training import create_surprise_dataset
from training import create_full_train
import pandas as pd

def get_top_n_for_user(user_df, original_df, original_model, n=10):
    """Return the top-N recommendation for our specific user from a set of predictions.

    Args:
        user_df: user's dataframe contain user_name, top_track, normalized rating
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dataframe that top 10 recommendations for user
    """

    original_df.append(user_df, ignore_index=True)
    surprise_data = create_surprise_dataset(original_df)
    trainset = create_full_train(surprise_data)
    new_model = original_model.fit(trainset)

    user_unknown_song = original_df[original_df.user != user_df.user]
    user_unknown_song_list = list(dict.fromkeys(user_unknown_song.song.tolist()))
    pred_list = []
    for song in user_unknown_song_list:
        pred_list.append(new_model.predict(user, song, verbose=True))

    user_pre_df = pd.DataFrame(pred_list, columns=['user', 'song', 'real_rating', 'est_rating', 'was_imporsible'])
    user_pre_df = user_pre_df.sort_values(by=['est_rating'], ascending=False).head(n).drop(columns=['real_rating', 'was_imporsible'])

    return user_pre_df