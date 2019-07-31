# IMPORT LIBRARIES
import pyzillow
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails 
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib
import os
import sys
from io import StringIO
from datetime import datetime



# ZILLOW API USER INFO----------------------------------------------------------

def sql_insert_function_zillow_api_data(mydb, val):
	print('Inserting zillow home data')
	mycursor = mydb.cursor()
	sql_command = '''
	INSERT INTO HOUSE_DETAILS (
		street_address, pull_date, zillow_id, home_type, 
		tax_year, tax_value, year_built, last_sold_date, last_sold_price, 
		home_size, property_size, num_bedrooms, num_bathrooms, 
		zillow_low_est, zillow_high_est, value_change, zillow_percentile)

	VALUES(	%s, %s, %s, %s, %s, %s, 
			%s, %s, %s, %s, %s, %s, 
			%s, %s, %s, %s, %s) 
	'''

	mycursor.execute(sql_command, val)
	mydb.commit()
	print('Zillow home data successfully inserted into db\n')
	return None


# GET DEEP SEARCH RESULTS-------------------------------------------------------
def get_house_data_zillow_api(address, zipcode, pull_date):
	''' Purpose:  Utilizing the zillow api to query data for a single house 
		Input:    Address and zipcode for a single house
		Output:	  None.  We will use insert statement within this function'''

	# User feedback
	print('Accessing Zillow API')
	
	# Instantiate connection to zillow database
	web_service_id  = 'X1-ZWz1h90xzgg45n_2kpit'
	documentation   = 'https://pypi.org/project/pyzillow/'
	d2				= 'https://anchetawern.github.io/blog/2014/03/20/getting-started-with-zillow-api/'
	zillow_data = ZillowWrapper(web_service_id)
	deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
	result = GetDeepSearchResults(deep_search_response)

	# Create Object for the old & new stdout
	old_stdout = sys.stdout	
	new_stdout = StringIO()
	sys.stdout = new_stdout	

	# Generate stdout - should redirect to StringIO	
	print('Key, Value')
	print('zillow_id,{}'.format(result.zillow_id))
	print('home_type,{}'.format(result.home_type))
	print('tax_year,{}'.format(result.tax_year))
	print('tax_value,{}'.format(result.tax_value)) 
	print('year_built,{}'.format(result.year_built))
	print('last_sold_date,{}'.format(result.last_sold_date))
	print('last_sold_price,{}'.format(result.last_sold_price)) 
	print('home_size,{}'.format(result.home_size))
	print('property_size,{}'.format(result.property_size))
	print('num_bedrooms,{}'.format(result.bedrooms))
	print('num_bathrooms,{}'.format(result.bathrooms))
	print('zillow_low_est,{}'.format(result.zestimate_valuationRange_low))
	print('zillow_high_est,{}'.format(result.zestimate_valuation_range_high))
	print('zillow_value_change,{}'.format(result.zestimate_value_change))
	print('zillow_percentile,{}'.format(result.zestimate_percentile))
				
	# Convert stdout from StringIO to String	
	new_stdout_str = new_stdout.getvalue()	
	test_stdout_str = open('zillow_api_data.csv', 'w')
	test_stdout_str.write(new_stdout_str)
	test_stdout_str.close()
	
	# Return to old stdout
	sys.stdout = old_stdout
	
	# Read CSV back in as a pandas dataframe
	df = pd.read_csv('zillow_api_data.csv')
	df.set_index('Key', inplace=True)

	# Need to convert values from strings to correct input value for db
	val_zillow_api = []

	val_zillow_api.append(address)
	val_zillow_api.append(pull_date)
	val_zillow_api.append(df.iloc[0,0])					# zillow_id
	val_zillow_api.append(df.iloc[1,0])					# home type
	val_zillow_api.append(df.iloc[2,0])					# tax year
	val_zillow_api.append(df.iloc[3,0])					# tax value
	val_zillow_api.append(df.iloc[4,0])					# year built
	# Try to append formatted datetime object.  
	try:
		val_zillow_api.append(datetime.strptime(df.iloc[5, 0], '%m/%d/%Y')) # last sold date
	# If None date append the arbitrary date of 01/01/1900
	except ValueError as err:
		print('Zillow api returned the following sold date => {}'.format(df.iloc[5,0]))
		print('Zillow api value error generated:  {}'.format(err))		
		val_zillow_api.append(datetime.strptime('01/01/1900', '%m/%d/%Y')) # last sold date

	val_zillow_api.append(df.iloc[6,0])					# last sold price	
	val_zillow_api.append(df.iloc[7,0])					# home size

	# Test if property value == none.  Appaned 0 if None. 
	if df.iloc[8,0] == None or df.iloc[8,0] == 'None':
		val_zillow_api.append(0)					# property size
	else:
		val_zillow_api.append(df.iloc[8,0])

	val_zillow_api.append(df.iloc[9,0])					# number bed rooms
	val_zillow_api.append(df.iloc[10,0])				# num bathrooms
	val_zillow_api.append(df.iloc[11,0])				# zillow_low_est
	val_zillow_api.append(df.iloc[12,0])				# zillow high est
	val_zillow_api.append(df.iloc[13,0])				# value change
	val_zillow_api.append(df.iloc[14,0])				# zillow percentile

	# Return List Object to be passed to sql insert function
	print('Zillow API data successfully obtained\n')
	return val_zillow_api

	


# GET UPDATED PROPERTY DETAILS------------------------------------------------
def zillow_id_search(zillow_id):
	updated_property_details_response = zillow_data.\
                                    get_updated_property_details(zillow_id)
	result = GetUpdatedPropertyDetails(updated_property_details_response)
	print('Home type       => {}'.format(result.home_type))
	print('Neighborhood    => {}'.format(result.neighborhood))
	print('School District => {}'.format(result.school_district))
	print('Basement        => {}'.format(result.basement))
	print('Roof            => {}'.format(result.roof))
	
	print('\n')
	
	return None






# TEST ZILLOW API
'''
address = '1175 Lea Drive'
zipcode = 30076


test = get_house_data_zillow_api(address, zipcode, '07/23/2019')
[print(x) for x in test]
'''





