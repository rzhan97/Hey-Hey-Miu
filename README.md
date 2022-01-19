# Hey Hey Miu


## Overview
Hey hey Miu is a web app that give you music recommendation based on your listening history, coded in python, powered by Flask and surprise package
## Motivation 
Music plays an important role in our life and music, And it always have a strong power by connecting us when we sharing songs and affect our emotion when we need motivation or a enjoyable cooking time.
During the pandemic, music sharing as a important factor in the social showing increase from the study, Based on those and my entusiation for the music， I would like to build an end-to-end music recommendation web app.


## Goals
Build a webapp that recommend music based on user's listening history and powered by machine learning algorithm SVD.(After compared with (KNN, NMF, SVD etc.)

## Datasets
Since there is not a complete dataset online about how real users' listening habit recently, I scraping the user name on LastFM website and get user's listen habits ,which is top tracks they recently listening from Lastfm API, and scale the times of a song they listen into a rating score.  
usersong_matrix_df saved in https://drive.google.com/file/d/1e9WlXgqsR1bhFBNPF6j1XfUIAzrXM5DW/view?usp=sharing

## How it works
![84171642604663_ pic](https://user-images.githubusercontent.com/37779983/150181600-dcad03c1-95cd-4b4a-85dd-7ee94c4ba9f8.jpg)

## Reference
Some other project inspired me:<br />

-It's a AI-powered music recommendation system, Pro: using machine learning technical and clean layout. Con: Not every song can be played on website https://www.gnoosic.com/ <br />
-A music recommandation website with clean structure, Pro: user-friendly layout, Con:Every playlist is curated by people, which is a demanding job for one person. https://noonpacific.com/los-angeles/noon-446<br />
-Projects using spotify API, which I will also use for this project webapp building. https://developer.spotify.com/discover/
-Surprise's author Nicolas Hug gave an amazing explaination on how SVD works and why it is popular http://nicolas-hug.com/blog/
