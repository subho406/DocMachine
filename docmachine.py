import os
import datetime
import urllib.parse, requests
# from sklearn import externals
# from sklearn.externals import joblib
import pickle as pk

# Web App libraries
from flask import Flask, jsonify, request

# Machine Learning Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pysftp
import threading
from libs import extract
from libs import db

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None    # disable host key checking.
sql=None
TRAINLIMIT = 1000000
DETECTINTERVAL = 100
CONFIDENCE = 10
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
app.config.update(
    PROPAGATE_EXCEPTIONS = True
)

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/api/post', methods=['POST'])
def Post():

    # Connect to database
    global sql
    if(sql==None):
        sql=db.dbconnect()
    # load the model from disk
    clf = pk.load(open('lab/clf.pkl', 'rb'))
    # clf = externals.joblib.load('lab/clf.pkl')

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
    is_checking = Detect(DETECTINTERVAL)

    return 'Elevator'+str(eID)+'<br>Anomaly'+str(anomaly)+'<br>Score'+str(score)+'<br>Count'+str(DATACOUNTS['Elevator01'])

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

def Detect(interval):
    global sql
    for key, value in DATACOUNTS.items():
        if (value>=interval):
            DATACOUNTS[key] = 0
            # Fetch real time
            df = db.get_realtime_data(sql, key, interval)
            
            anomalies = 0
            for i in df:
                if (i['anomaly']==-1):
                    anomalies+=1
            anomaly_prcnt = (anomalies/interval) * 100

            print('Score'+str(anomaly_prcnt))

            if(anomaly_prcnt>=CONFIDENCE):
                thread = threading.Thread(target=push_anomaly_data, args=(key,df,anomaly_prcnt))
                thread.daemon = True                            # Daemonize thread
                thread.start()                                  # Start the execution
                #push_anomaly_data(key,df,anomaly_prcnt)
            else:
                continue

def upload_file(file):
    with pysftp.Connection('sp-do-blr1-1.li8.in', username='serverpilot', password='b1ttup@d@mdi', cnopts=cnopts) as sftp:
        with sftp.cd('/srv/users/serverpilot/apps/kone/public/files/'):             # temporarily chdir to public
            sftp.put(file)  # upload file to public/ on remote


def push_anomaly_data(elevator_id,data,anomaly_prcnt):
    sql=db.dbconnect()
    # Making dataframe
    df = pd.DataFrame(data)
    # Preparing data visualisations
    sns.set(color_codes=True)
    print('Timestamp: {:%Y-%b-%d %H:%M:%S}'.format(datetime.datetime.now()))

    # Pair plot
    sns.set(color_codes=True)
    pair=sns.pairplot(df,vars=["motor_temp", "cabin_speed", "motor_vibration","current"],hue="inner_motor_temp",palette="husl")
    pairfile='pair{:%Y-%b-%d%H-%M-%S}.png'.format(datetime.datetime.now())    
    pair.savefig(pairfile)
    plt.close(pair.fig)
    upload_file(pairfile)
    os.remove(pairfile)

    # Heat Map
    # relation = df.corr()
    # plt.figure(figsize=(12,12))
    # heatmap = sns.heatmap(relation, vmax=1, square=True, annot=True,fmt='.0g')
    # heatmap.figure.savefig('heat.png')


    # Box plot
    box = sns.boxplot(x="anomaly", y="score", data=df)
    box = sns.swarmplot(x="anomaly", y="score", data=df, color=".25")
    boxfile='box{:%Y-%b-%d-%H-%M-%S}.png'.format(datetime.datetime.now())    
    box.figure.savefig(boxfile)
    upload_file(boxfile)
    os.remove(boxfile)

    # Summary
    desc=df.describe()
    sumfile='sum{:%Y-%b-%d-%H-%M-%S}.csv'.format(datetime.datetime.now())
    desc.to_csv(sumfile)
    upload_file(sumfile)
    os.remove(sumfile)
    
    row={}
    row['elevator_id']=elevator_id
    row['score']=anomaly_prcnt
    row['hist']=pairfile
    row['heatmap']=pairfile
    row['matrix']=boxfile
    row['summary']=sumfile
    row['solved']=0
    db.insert_anomaly_data(sql,row)

    if(anomaly_prcnt>=85):
        # Send SMS notification
        payload = {'authkey':'116912AED4ipze5767efb1','mobiles':'919790706993,919787972333', 'message':'AInstein detected Anomaly in '+str(elevator_id)+'. Attention Required', 'sender':'KBECOM', 'route':4, 'country':91}
        payload = urllib.parse.urlencode(payload)
        req=requests.post('https://control.msg91.com/api/sendhttp.php?'+payload)
    
    print('pushed anomaly')
    
    return True



port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))