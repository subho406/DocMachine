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

app = Flask(__name__, static_url_path='')


@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/post', methods=['POST'])
def Post():
    global sql
    raw = request.json
    db.insert_realtime_data(sql, raw)
    # Converting to dataframe
    df = extract.dict_to_dataframe(raw)
    # Storing Data frame for Training
    StoreData(df)
    data=raw['id']
    data=db.get_realtime_data(sql,10000)
    return str(data)

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

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    global sql
    sql = db.dbconnect()
    app.run(host='0.0.0.0', port=int(port))