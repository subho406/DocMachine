import os
import pickle as pk

# Web App libraries
from flask import Flask, jsonify, request

# Machine Learning Libraries
import pandas as pd
import numpy as np

from libs.extract import *

TRAINLIMIT 300

app = Flask(__name__, static_url_path='')

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/post', methods=['POST'])
def Post():
    raw = request.json
    StoreData(raw)
    return str(df.to_html())

def StoreData(rawdata):
    global data
    # Store Data till Train Limit
    if(data.shape[0]<=TRAINLIMIT):
        # Converting to dataframe
        df = dict_to_dataframe(rawdata)
        data = data.append(df, ignore_index=True)
        # Pickling the dataframe
        data.to_pickle('static/data/data.pkl')

port = os.getenv('PORT', '5000')
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(port))