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




# ZILLOW API USER INFO----------------------------------------------------------

# INSERT STATEMENT--------------------------------------------------------------

def sql_insert_function_zillow_api_data(mydb, val):
	print('Inserting zillow home data')
	mycursor = mydb.cursor()
	sql_command = '''
	INSERT INTO HOUSE_DETAILS (
		street_address, pull_date, zillow_id, home_type, 
		tax_year, tax_value, year_built, last_sold_date, last_sold_price, 
		home_size, property_size, num_bedrooms, num_bathrooms, 
		zillow_low_est, zillow_high_est, value_change, zillow_percentile, url)

		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		'''
	#****REmoved state added url
	mycursor.execute(sql_command, val)
	mydb.commit()
	print('Zillow home data successfully inserted into db')
	return None


# GET DEEP SEARCH RESULTS-------------------------------------------------------
def get_house_data_zillow_api(address, zipcode, pull_date, url):
	''' Purpose:  Utilizing the zillow api to query data for a single house 
		Input:    Address and zipcode for a single house
		Output:	  None.  We will use insert statement within this function'''

	# User feedback
	print('Start API Search')
	
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
	val_zillow_api.append(int(df.loc['zillow_id']))
	val_zillow_api.append(df.loc['home_type'])
	val_zillow_api.append(int(df.loc['tax_year']))
	val_zillow_api.append(round(float(df.loc['tax_value']), 0))
	val_zillow_api.append(int(df.loc['year_built']))
	val_zillow_api.append(df.loc['last_sold_date'])
	val_zillow_api.append(int(df.loc['last_sold_price']))
	val_zillow_api.append(int(df.loc['home_size']))
	val_zillow_api.append(int(df.loc['property_size']))
	val_zillow_api.append(int(df.loc['num_bedrooms']))
	val_zillow_api.append(round(float(df.loc['num_bathrooms']), 0))
	val_zillow_api.append(int(df.loc['zillow_low_est']))
	val_zillow_api.append(int(df.loc['zillow_high_est']))
	val_zillow_api.append(float(df.loc['zillow_value_change']))
	val_zillow_api.append(float(df.loc['zillow_percentile']))
	val_zillow_api.append(url)

	# Return List Object to be passed to sql insert function
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
address = '1175 Lea Drive'
zipcode = 30076


test = get_house_data_zillow_api(address, zipcode, '07/23/2019', 'zillow.com')
print(test)







