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
		street_address, state, pull_date, zillow_id, home_type, 
		tax_year, tax_value, year_built, last_sold_date, last_sold_price, 
		home_size, property_size, num_bedrooms, num_bathrooms, 
		zillow_low_est, zillow_high_est, value_change, zillow_percentile)

		VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		'''

	mycursor.execute(sql_command, val)
	mydb.commit()
	print('Zillow home data successfully inserted into db')
	return None


# GET DEEP SEARCH RESULTS-------------------------------------------------------
def get_house_data_zillow_api(address, zipcode):
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

	
	# Convert stdout to StringIO
	Dict = {}	
	old_stdout = sys.stdout
	result_str_io = StringIO
	sys.stdout = result_str_io
	# Send output to result object
	print(StringIO(result.zillow_id))
	Dict['zillow_id'] = str(result_str_io.getvalue())

	print('Dictionary = {}'.format(Dict))
	
	


	# Define a list of variables to print
	'''
	list_results = [('zillow_id', result.zillow_id), ('home_type', result.home_type), 
					('tax_year', result.tax_year), ('tax_year', result.tax_year), 
					('tax_value', result.tax_value), ('year_built', result.year_built), 
					('last_sold_date', result.last_sold_date), 
					('last_sold_price', result.last_sold_price), ('home_size', result.home_size),					 ('property_size', result.property_size), 
					('num_bedrooms', result.bedrooms), ('num_bathrooms', result.bathrooms),
					('zestimate_value_range_low', result.zestimate_valuation_range_low), 
					('zestimate_value_range_high', result.zestimate_valuation_range_high), 
					('zestimate_value_change', result.zestimate_value_change), 
					('zestimate_percentile', result.zestimate_percentile)
					]
		
	# Create Dictionary to hold values
	Dict_house_data = {}
	
	# Iterate list & add output to dictionary
	
	for value in list_results:
		
		# Convert stdout to StringIO
		old_stdout = sys.stdout
		result = StringIO
		sys.stdout = result
		# Send output to result object
		print(value[1])
		# Add result and name to dictionary
		Dict_house_data[value[0]] = result
		print(Dict_house_data)	
		print('1')	
	print('Creating list of housing data\n')
	# Return val_home_data
	return val_home_data
	'''




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



