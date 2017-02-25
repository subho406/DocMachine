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
	timestamp = datetime.datetime.today()
	timestamp=str(timestamp.year)+'-'+str(timestamp.month)+'-'+str(timestamp.day)+' '+str(timestamp.hour)+':'+str(timestamp.minute)+':'+str(timestamp.second)
	row['timestamp']=timestamp
	cur = db.cursor()
	with open(config_file) as data_file:    
		data = json.load(data_file)
	columns=data['Realtimecols']
	query = 'INSERT INTO Realtime VALUES ('
	for col in columns:
		query=query+'"'+str(row[col])+'",'
	query=query[:(len(query)-1)]+')'
	cur.execute(query)
	db.commit()


#Get realtime data before seconds
#
#Input: db, seconds
#output: Array of dicts containing the rows
def get_realtime_data(db,seconds):
	timestamp = datetime.datetime.today()-datetime.timedelta(seconds=seconds)
	timestamp=str(timestamp.year)+'-'+str(timestamp.month)+'-'+str(timestamp.day)+' '+str(timestamp.hour)+':'+str(timestamp.minute)+':'+str(timestamp.second)
	query='SELECT * from Realtime where timestamp>%s;'%(timestamp)
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