import os
import pickle as pk

# Web App libraries
from flask import Flask, jsonify, request

# Machine Learning Libraries
import pandas as pd
import numpy as np

from libs import extract
from libs import db

TRAINLIMIT = 1000000
DETECTINTERVAL = 100
DATACOUNTS={'Elevator00':0,
            'Elevator01':0,
            'Elevator02':0,
            'Elevator03':0,
            'Elevator04':0,
            'Elevator05':0,
            'Elevator06':0,
            'Elevator07':0,
            'Elevator08':0,
            'Elevator09':0,
            'Elevator10':0}

app = Flask(__name__, static_url_path='')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/post', methods=['POST'])
def Post():
    # Connect to database
    global sql
    sql = db.dbconnect()

    # load the model from disk
    clf = pk.load(open('lab/clf.pkl', 'rb'))

    # Processing the request
    raw = request.json

    # Converting to dataframe
    df = extract.dict_to_dataframe(raw)
    # Storing Data frame for Training
    StoreData(df)
    
    # Detecting Anomaly
    anomaly = clf.predict(df)
    score = float(clf.decision_function(df))
    raw['anomaly'] = int(anomaly)
    raw['score'] = score

    # Insert into real time table
    db.insert_realtime_data(sql, raw)

    eID=raw['id']
    DATACOUNTS[eID] += 1

    # Checking at intervals
    is_checking = Detect(DETECTINTERVAL, sql)

    return str(eID)+str(is_checking)

@app.route('/api/delmodel', methods=['GET'])
def Delete():
    os.remove("static/data/data.csv")
    return 'Removed Bitch!'

def StoreData(newdata):
    # Check if storage exists
    if(os.path.isfile('static/data/data.csv')):
        if(os.stat('static/data/data.csv').st_size<TRAINLIMIT):
            with open('static/data/data.csv', 'a') as f:
                newdata.to_csv(f, header=False, index=False)
        
    else:
        # Defining a new data frame
        dffloatcols=['motor_temp','load','cabin_speed','inner_motor_temp','motor_vibration','current']  
        dfcatcolsraw=['state','direction']
        dfcatcols=['state_moving','state_loading','state_idle','state_stopped','direction_1','direction_0','direction_-1']      
        data=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)

        # Append and store
        data = data.append(newdata)
        data.to_csv('static/data/data.csv',index=False)

def Detect(interval, sql):
    for key, value in DATACOUNTS.iteritems():
        if (value>=interval):
            value = 0
            # Push anomaly into database
            return True
        
        else:
            return False


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    global sql
    sql = db.dbconnect()
    app.run(host='0.0.0.0', port=int(port))