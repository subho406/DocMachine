import os
import pickle as pk

# Web App libraries
from flask import Flask, jsonify, request

# Machine Learning Libraries
import pandas as pd
import numpy as np

from libs.extract import *

TRAINLIMIT = 30

app = Flask(__name__, static_url_path='')

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/post', methods=['POST'])
def Post():
    raw = request.json

    # Converting to dataframe
    df = dict_to_dataframe(raw)

    # Storing Data frame for Training
    try:
        StoreData(df)
    except(e):
        return (e)

    return str(df.to_html())

def StoreData(newdata):
    # Check if storage exists
    if(os.path.isfile('static/data/data.pkl')):
        olddata = pd.read_pickle('static/data/data.pkl')
        # Store Data till Train Limit
        if(olddata.shape[0] < TRAINLIMIT):
            olddata = olddata.append(newdata, ignore_index=True)
            # Pickling the dataframe
            olddata.to_pickle('static/data/data.pkl')
        else:
            print('Limit Reached')
    
    else:
        # Defining a new data frame
        dffloatcols=['motor_temp','load','cabin_speed','inner_motor_temp','motor_vibration','current']  
        dfcatcolsraw=['state','direction']
        dfcatcols=['state_moving','state_loading','state_idle','state_stopped','direction_1','direction_0','direction_-1']      
        data=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)

        # Append and store
        data = data.append(newdata)
        data.to_pickle('static/data/data.pkl')

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))