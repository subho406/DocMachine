import os
import pandas as pd
import numpy as np
import pymysql
import json
import datetime


config_file='config.json'

#Database connection functions
#
#Connect to database
#Database details in config.json
#
def dbconnect():
	with open(config_file) as data_file:    
		data = json.load(data_file)
	Host=data['mysql']['URL']
	User=data['mysql']['USER']
	Passwd=data['mysql']['PASSWORD']
	Db=data['mysql']['DATABASE']
	db = pymysql.connect(host=Host, user=User, passwd=Passwd, db=Db)
	return db

#Insert data to the realtime database
# 
#Input: (db: db, row: dict)
#

def insert_realtime_data(db,row):
	timestamp = datetime.datetime.now()
	timestamp=str(timestamp.year)+'-'+str(timestamp.month)+'-'+str(timestamp.day)+' '+str(timestamp.hour)+':'+str(timestamp.minute)+':'+str(timestamp.second)+' +00:00'
	row['timestamp']=timestamp
	cur = db.cursor()
	with open(config_file) as data_file:    
		data = json.load(data_file)
	columns=data['Realtimecols']
	query = 'INSERT INTO Realtime VALUES ('
	for col in columns:
		query=query+'"'+str(row[col])+'",'
	query=query[:(len(query)-1)]+')'
	print(query)
	cur.execute(query)
	db.commit()
#Insert data to the Anomaly database
# 
#Input: (db: db, row: dict)
#
def insert_anomaly_data(db,row):
	timestamp = datetime.datetime.now()
	timestamp=str(timestamp.year)+'-'+str(timestamp.month)+'-'+str(timestamp.day)+' '+str(timestamp.hour)+':'+str(timestamp.minute)+':'+str(timestamp.second)+' +00:00'
	row['time']=timestamp
	cur = db.cursor()
	with open(config_file) as data_file:    
		data = json.load(data_file)
	columns=data['Anomalycols']
	query = 'INSERT INTO Anomaly (elevator_id, score, hist, heatmap, matrix, summary, time, solved ) VALUES ('
	for col in columns:
		query=query+'"'+str(row[col])+'",'
	query=query[:(len(query)-1)]+')'
	print(query)
	cur.execute(query)
	db.commit()	
#Get realtime data before seconds
#
#Input: db, id: ID of Elevator, last: number of records to fetch from tail
#output: Array of dicts containing the rows
def get_realtime_data(db,id,last):
	query='SELECT * from Realtime where id="%s" order by timestamp desc limit %d;'%(id,last)
	cur=db.cursor()
	cur.execute(query)
	temp=cur.fetchall()
	with open(config_file) as data_file:    
		data = json.load(data_file)
	columns=data['Realtimecols']
	results=[]
	rowcount=-1
	for row in temp:
		rowcount=rowcount+1
		results.append(dict())
		for i in range(0,len(columns)):
			results[rowcount][columns[i]]=row[i]
	return results

#Database connection 