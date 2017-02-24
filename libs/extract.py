import os
import pandas as pd
import numpy as np

"""
from flask import Flask, render_template, request
import cf_deployment_tracker

# Emit Bluemix deployment event
cf_deployment_tracker.track()
app = Flask(__name__)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('PORT', 8080))
"""

#---------------- Library functions start -------------------------

#Data schema definitions. All Training features will be declared here.
#Feature transformation should be done both before training and test
#
#Continuous valued features
dffloatcols=['motor_temp','load','cabin_speed','inner_motor_temp','motor_vibration','current'] 	
#Categorical features
dfcatcolsraw=['state','direction']
dfcatcols=['state_moving','state_loading','state_idle','state_stopped','direction_1','direction_0','direction_-1']		
#Feature Transformation function 
# Input: pandas.DataFrame
# Output: pandas.DataFrame
data=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)
def normalise(df): 
	#Log Transformation
	df[dffloatcols]=np.log1p(df[dffloatcols].astype('float64'))
	return df

#Function that converts json data received from http request
#to a dataframe with all feature transformations
# Input: dict
# Output: pandas.DataFrame of columns dffloatcols+dfcatcols
def dict_to_dataframe(req):
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
	df=normalise(df)
	return df
#Library functions end

'''
@app.route('/', methods = ['GET','POST'])
def server():
	req=request.json
	global data
	if(data.shape[0]>20):
		data=pd.DataFrame(None,None,columns=dffloatcols+dfcatcols)
	df=dict_to_dataframe(req)
	data=data.append(df)
	return str(data.to_html())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
'''