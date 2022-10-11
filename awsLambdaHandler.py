#Load the required modules
import pymysql
import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
import numpy as np

#Establish a connection to the database
#Note, keep this outside the handler to ensure we recycle connections to the database for multiple calls.
connection = pymysql.connect(host = endpoint, user = username, password = password, db = database_name)

#Decalre a function to convert regression output from our knn model to a classificaiton output
def convert_to_classification(input_predictions):
    output_classes = []

    for item in input_predictions:
        if item < 180:
            output_classes.append('3')
        #elif item < 1200:
        #    output_classes.append('moderate')            
        else:
            output_classes.append('4')

    return output_classes

#Decalre a fucntion to parse the incoming waypoints from the app
def parse_coordinates(incoming_string):
    results = []
    incoming_string = incoming_string.replace(' ','')
    
    coordinate_list = incoming_string.split('),(')

    coordinate_list = [x.replace('(','') for x in coordinate_list]
    coordinate_list = [x.replace(')','') for x in coordinate_list]
    coordinate_list = [x.replace('}','') for x in coordinate_list]
    coordinate_list = [x.replace('"','') for x in coordinate_list]
    coordinate_list = [x.replace("'",'') for x in coordinate_list]

    for coords in coordinate_list:
        split_coords = coords.split(',')
        try:
            split_coords = [float(x) for x in split_coords]
        except:
            continue
        
        results.append(tuple(split_coords))

    return results

#Decalre the lambda handler. This is the funciton that will be invoked by lambda
def lambda_handler(event, context):
    
    #Parse the waypoints incoming from the app
    waypoints = event['queryStringParameters']['waypoints']
    
    #Convert the waypoints to a dataframe and add in the required features.
    prediction_x = pd.DataFrame(parse_coordinates(incoming_string = waypoints), columns =['lat','lon'])
    prediction_x['date'] = pd.to_datetime("today").strftime("%Y/%m/%d/ %H")
    prediction_x['unix_time'] = pd.to_datetime(prediction_x.date).astype(np.int64) // 10**9

    prediction_x['month'] = pd.DatetimeIndex(prediction_x['date']).month
    prediction_x['hour'] = pd.DatetimeIndex(prediction_x['date']).hour
    prediction_x['day_of_week'] = pd.DatetimeIndex(prediction_x['date']).dayofweek
    prediction_x['position'] = prediction_x.lon * prediction_x.lat

    prediction_x = prediction_x[['unix_time','hour','month','day_of_week','position']]
    
    #Create a cursor object to interact with the MySQL database
    cursor = connection.cursor()
    
    #Define sql query to pull in all the data from the MySQL database
    sql = 'SELECT * FROM pedestrianCount'
    
    #Read the query data into a dataframe
    df = pd.read_sql(sql, connection)
    
    #Add the required attributes to the training data
    df['date'] = pd.to_datetime(df['unix_time'],unit='s')
    df['position'] = df.lon * df.lat
    df['month'] = df.date.dt.month
    df['day_of_week'] = df.date.dt.dayofweek
    df = df[['sensor_id','count', 'unix_time','hour','month','day_of_week','position','date']]
    
    df_y = df['count']
    df.drop(['count', 'sensor_id','date'], axis = 1, inplace = True)
    
    #Define a scalar to standardise the magnitude of the training and test data
    ss = StandardScaler()
    
    #Scale the training data
    df = ss.fit_transform(df)
    #Scale the test data
    prediction_x = ss.transform(prediction_x)
    
    #Create a KNN object with k = 9. This is determined based on local model selection.
    knn = KNeighborsRegressor(n_neighbors = 9)
    #Fit the KNN model to the training data
    knn.fit(df, df_y)
    
    #Make a prediction on the incoming data
    prediction = convert_to_classification(knn.predict(prediction_x))
    #Set the prediction as the mode of the predictions
    prediction = max(set(prediction), key=prediction.count)
    
    #Create the response object
    response = {}
    response['result'] = prediction
    
    responseObject = {}
    responseObject['statusCode'] = 200
    responseObject['headers'] = {}
    responseObject['headers']['Content-Type'] = 'application/json'
    responseObject['body'] = json.dumps(response)
    
    #Return the object to the api gateway to be returned to the user
    return responseObject
