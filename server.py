from flask import Flask, render_template, request, send_from_directory
from libs import db
import cf_deployment_tracker
import os
import pandas as pd
import numpy as np
import pymysql
import json
array=[]
count=0

#Helper function to dump data to file
def outputtotext(req):
	array.append(req)
	global count
	count=count+1
	if count<2000:
		with open('data.txt', 'w') as outfile:
			outfile.write(str(array))
	else:
		exit()

# Emit Bluemix deployment event
cf_deployment_tracker.track()
app = Flask(__name__,static_url_path='')

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('PORT',5000 ))


#Library functions start
#Data schema definitions. All Training features will be declared here.
#Feature transformation should be done both before training and test
#
#Continuous valued features
dffloatcols=['motor_temp','load','cabin_speed','inner_motor_temp','motor_vibration','current'] 	
#Categorical features
dfcatcolsraw=['state','direction']
#Categorical features broken down
dfcatcols=['state_moving','state_loading','state_idle','state_stopped','direction_1','direction_0','direction_-1']		
#Feature Transformation function 
# Input: pandas.DataFrame
# Output: pandas.DataFrame
data=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)

def normalise(df,dffloatcols): 
	#Log Transformation
	df[dffloatcols]=np.log1p(df[dffloatcols].astype('float64'))
	return df

#Function that converts json data received from http request
#to a dataframe with all feature transformations
# Input: (req: dict, dffloatcols, dfcatcols, dfcatcolsraw : Array of string)
# Output: pandas.DataFrame of columns dffloatcols+dfcatcols
def dict_to_dataframe(req,dffloatcols,dfcatcols,dfcatcolsraw):
	#Generate empty DataFrame
	df=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)
	#Set all categorical features values to 0
	df.loc[0,dfcatcols]=0
	#Set the activated categorical value to 1
	for d in dfcatcolsraw:
		df.loc[0,d+'_'+str(req[d])]=1
	#Assign all numeric features
	for d in dffloatcols:
		df.loc[0,d]=int(req[d])	
	#Normalise numeric features
	df=normalise(df,dffloatcols)
	return df

@app.route('/', methods = ['POST'])
def server():
	req=request.json
	global sql
	data=db.get_realtime_data(sql,100000)
	return data


if __name__ == '__main__':
	global sql
	sql=db.dbconnect()
	app.run(host='0.0.0.0', port=port, debug=True)


	
