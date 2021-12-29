#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021-12-27
@author: zoe
"""
from surprise import Dataset
from surprise import Reader
from surprise import SVD
from surprise.model_selection import GridSearchCV

def create_surprise_dataset(df, user, item, rating, rating_scale):
    """
    Funtion for creating the suprise dataset from pandas dataframe
    :param pandas df:
    :param user:
    :param item:
    :param rating:
    :param rating_scale:
    :return:
    """
    reader = Reader(rating_scale=rating_scale)
    surprise_data = Dataset.load_from_df(df[[user, item, rating]], reader)
    return surprise_data


def run_grid_search(surprise_data):
    '''
    Function for running GridSearchCV algorithm tuning.
    params: surprise_data (surprise dataset), algo (surprise recommender algorithm),
    param_grid (dictionary, tuning parameters), scraper_run (string)
    :returns gs_results (dataframe), gs_run (string), best_params (dictionary)
    '''
    param_grid = {'n_epochs': [10, 20], 'lr_all': [0.002, 0.005, 0.1],
                  'reg_all': [0.1, 0.5]}
    gs = GridSearchCV(SVD, param_grid, measures=["rmse"], cv=3)
    gs.fit(surprise_data)
    best_params = gs.best_params["rmse"]

    return best_params

#Function for creating surprise train and testset
def create_train_and_test(surprise_data, test_size):
    '''
    Function for creating a training and testing dataset from surprise data.
    params: surprise_data (surprise dataset), test_size (float)
    :returns trainset (surprise trainset object), testset (surprise testset object)
    '''
    trainset, testset = train_test_split(surprise_data, test_size)
    return trainset, testset

# Function for running simple implementation of SVD
def run_model(trainset, testset, best_params):
    '''
    Function for running surprise's SVD algorithm
    params: trainset (surprise trainset), testset (surprise testset), best_params (dict)
    :returns svd_fit (fitted SVD model), predictions (defaultdict), test_rmse (float)
    '''

    algo = SVD(n_factors=best_params["n_factors"], n_epochs=best_params["n_epochs"],
               lr_all=best_params["lr_all"], reg_all=best_params["reg_all"])
    svd_fit = algo.fit(trainset)
    predictions = svd_fit.test(testset)
    test_rmse = accuracy.rmse(predictions)
    return svd_fit, predictions, test_rmse

def get_top_n(predictions, n=10):
    """Return the top-N recommendation for each user from a set of predictions.

    Args:
        predictions(list of Prediction objects): The list of predictions, as
            returned by the test method of an algorithm.
        n(int): The number of recommendation to output for each user. Default
            is 10.

    Returns:
    A dict where keys are user (raw) ids and values are lists of tuples:
        [(raw item id, rating estimation), ...] of size n.
    """

    # First map the predictions to each user.
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))

    # Then sort the predictions for each user and retrieve the k highest ones.
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]

    return top_n

if __name__ == "__main__":
    """
    Training the best model
    """
    # load the processed data
    load_df = pd.read_pickle("../data/processed/userrating_df")
    surprise_data = create_surprise_dataset(load_df,'user', 'song','new_rating', rating_scale=(1, 5))

    # define the path for model and feature transformer
    model_path="../models/lr_final_model.pkl"
    transformer_path="../models/transformer.pkl"

    #Merging the training and validation data together to train the final best model
    labelEncoder = LabelEncoder()
    frames = [train_news, val_news]
    train_val = pd.concat(frames)
    train_val['label'].value_counts()
    train_val['label'] = labelEncoder.fit_transform(train_val['label'])

    # training final model
    field='statement'
    LogR_clf_final = LogisticRegression(verbose=1, solver='liblinear',random_state=0, C=5, penalty='l2',max_iter=1000)
    lr_final_model,transformer=train_final_model(LogR_clf_final,train_val,field=field,feature_rep='counts')
    # save model
    # we need to save both the transformer -> to encode a document and the model itself to make predictions based on the weight vectors
    pickle.dump(lr_final_model,open(model_path, 'wb'))
    pickle.dump(transformer,open(transformer_path,'wb'))

    print("best model saved in ", model_path)