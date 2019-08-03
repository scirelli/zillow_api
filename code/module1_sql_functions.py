import re
import sys
from io import StringIO
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib
from time import sleep
from datetime import datetime
import random
import mysql.connector
import pyzillow
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails



# MYSQL - CLEAR TABLE FUNCTION-----------------------------------------
def clear_table(mydb, decision = 'No'):

    if decision == 'Yes' or decision == 'yes':

        # Delete Addresses Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM ADDRESSES;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'Addresses' table")

        # Delete House Details Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM HOUSE_DETAILS;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'House Details' table")

        # Delete Schools Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM SCHOOLS;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'Schools' table\n")

    elif decision == 'No' or decision == 'no':
        # Do Not Delete Table Data
        print('''Data will not be cleared from the Addresses, 
                 House details and Schools tables\n''')

    # Return None
    return None



# ADDRESS INSERT FUNCTION ------------------------------------------------
def sql_insert_function_addresses(mydb, val):
	try:
		#print('Inserting address information into db')
		mycursor = mydb.cursor()
		sql_command = '''
					INSERT IGNORE INTO ADDRESSES (
					street_address, state, zipcode, city, pull_date, url)
                    VALUES(%s, %s, %s, %s, %s, %s)'''

		mycursor.execute(sql_command, val)
		mydb.commit()
		#print('Address information successfully inserted\n')
		return None
	
	except mysql.connector.errors.ProgrammingError as err:
		print('sql insert addresses function generated an error => {}'.format(err))

	except mysql.connector.errors.IntegrityError as err:
		print('sql insert addresses function generated an error => {}'.format(err))


# SCHOOL RANKING INSERT FUNCTION -----------------------------------------
def sql_insert_function_schools(mydb, val, street_address, pull_date, url):
	#print('Inserting school ranking data')

	if val != None:
		if len(val) < 3:
			print('Less than three school rankings scraped. Returning 0,0,0')
			return [0,0,0]

		# If its not, lets proceed with the insertion. 
		else:
			try:
				mycursor = mydb.cursor()
				sql_command = '''
				INSERT IGNORE INTO SCHOOLS (

                    street_address, pull_date,  
                    elementary_school_rating, middle_school_rating, 
                    high_school_rating, url) 
                    
                    VALUES(%s, %s, %s, %s, %s, %s)'''
				val_insert = [street_address, pull_date, 
						  val[0], val[1], val[2], url]
				mycursor.execute(sql_command, val_insert)
				mydb.commit()
				#print('School information successfully inserted\n')

			except mysql.connector.errors.ProgrammingError as err:
				print('sql insert schools function generated an error => {}'.format(err))
				print('sql insert schools function generated an error => {}'.format(err))


# ZILLOW API INSERT FUNCTION --------------------------------------------------
def replace_none_values(val):
	# ** Note that we need to figure out a way to not have this apply to the dates
	# Define new list object
	new_val = []
	if val != None:
		for value in val:
			if value == None or value == 'None':
				new_val.append(0)
			else:
				new_val.append(value)

	return new_val
		

def sql_insert_function_zillow_api_data(mydb, val):
	#print('Inserting zillow home data')
	mycursor = mydb.cursor()
	sql_command = '''
    INSERT IGNORE INTO HOUSE_DETAILS (
        street_address, pull_date, zillow_id, home_type, 
        tax_year, tax_value, year_built, last_sold_date, last_sold_price, 
        home_size, property_size, num_bedrooms, num_bathrooms, 
        zillow_low_est, zillow_high_est, value_change, zillow_percentile, asking_price)

    VALUES( %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s) 
    '''
	try:
		mycursor.execute(sql_command, replace_none_values(val))
		mydb.commit()
		#print('Zillow home data successfully inserted into db\n')
	except mysql.connector.errors.ProgrammingError as err:
		print('Zillow insert function geneted an error => {}'.format(err))

	except mysql.connector.errors.IntegrityError as err:
		print('sql insert zillow function generated an error => {}'.format(err))


	return None





# GET GEORGIA MUNICIPAL DATA

def get_ga_muni_data(mydb):
	sql_command = '''SELECT 
					 NAME, TYPE, COUNTY 
					 FROM GA_MUNICIPALITIES 
					 WHERE TYPE = 'Town';
				  '''
	df = pd.read_sql(sql_command, mydb)
	return df





