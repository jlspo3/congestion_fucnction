MyVis is a tool that allows for haptic navigational feedback to allow for a non-verbal navigational information to be transmitted to users. The concept specifically intented to integrate haptic feedback into a probing cane which connects with an android app for navigation data. The project is a proof of concept and not intended for use or distribution.

This repository contains the prototyping code to parse incoming pedestrian count data, train and KNN model on this pedestrian data and then deploy the model to an AWS lamnbda and MySQL database. Prerequisites:

Raspberry Pi OS / 2022-09-06
Python 3.9
SkLearn 1.1.2
An AWS account (RDS MySQL database, AWS Lambda function, AWS API Gateway)

Reccomended installation is
For AWS:
1. Configure AWS API Gateway to Trigger a lambda function
2. In this lambda fucntion, copy the 'awsLambdaHandler.py' code from this repository

For model training and selection:
1. Download the latest pedestrian count data from https://www.melbourne.vic.gov.au/about-melbourne/research-and-statistics/city-population/Pages/pedestrian-counting-system.aspx
2. run data_parse.ipynb with the data
3. run knn_algorithm.ipynb to train the model
4. run model_review.ipynb to review the training results and select a model
