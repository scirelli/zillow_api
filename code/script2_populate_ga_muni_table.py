import pandas as pd
import mysql.connector
import os

# USER INPUT-------------------------------------------------------------------------
user_name = 'ccirelli2' #input('user name:  ')
password  = 'Work4starr' #input('password :  ')
mysql_db  = 'HOUSING_DATA'#input('database :  ')

# INSTANTIATE CONNECTION TO MYSQL DATABASE--------------------------------------------
mydb = mysql.connector.connect(
                host='localhost',
                user= user_name,
                passwd= password,
                database= mysql_db)



def sql_insert_function_muni_data(mydb, val):

	mycursor = mydb.cursor()
	sql_command = '''
					INSERT IGNORE INTO GA_MUNICIPALITIES (
					NAME, TYPE, COUNTY)
					VALUES (%s, %s, %s)'''
	mycursor.execute(sql_command, val)
	mydb.commit()
	return None

os.chdir('/home/ccirelli2/Desktop/repositories/zillow_api/data')
df_data = pd.read_excel('ga_municipalities.xlsx')

for row in df_data.itertuples():
	val = [row[1], row[2], row[3]]
	sql_insert_function_muni_data(mydb, val)



