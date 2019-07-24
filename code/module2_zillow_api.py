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

# IMPORT MODULES----------------------------------------------------------------
#import module1_zillow_api as m1


# ZILLOW API USER INFO----------------------------------------------------------
user_name       = input('Input zillow api user name: ')
pswd            = input('Input zillow api password : ')
web_service_id  = 'X1-ZWz1h90xzgg45n_2kpit'
documentation   = 'https://pypi.org/project/pyzillow/'
d2				= 'https://anchetawern.github.io/blog/2014/03/20/getting-started-with-zillow-api/'
zillow_data = ZillowWrapper(web_service_id)

# INSERT STATEMENT--------------------------------------------------------------

def sql_insert_function_home_data(mydb, val):
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
	return None


# GET DEEP SEARCH RESULTS-------------------------------------------------------
def get_house_data_zillow_api(address, zipcode):
	''' Purpose:  Utilizing the zillow api to query data for a single house 
		Input:    Address and zipcode for a single house
		Output:	  None.  We will use insert statement within this function'''

	# Instantiate connection to zillow database
	deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
	result = GetDeepSearchResults(deep_search_response)
	
	# Define Output Value
	val_home_data = [result.zillow_id, 
					result.home_type, 
					result.tax_year,
					result.tax_value, 
					result.year_built, 
					result.last_sold_date, 
					result.last_sold_price, 
					result.home_size, 
					result.property_size,
					result.bedrooms, 
					result.bathrooms, 
					result.zestimate_value_range_low, 
					result.zestimate_valuation_range_high, 
					result.zestimate_value_change, 
					result.zestimate_percentile]

	# Return val_home_data
	return val_home_data
	






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

