
# IMPORT LIBRARIES
import pyzillow
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails 
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib



# IMPORT MODULES
import module1_zillow_api as m1



user_name       = 'ccirelli2'
pswd            = 'Work4starr'
web_service_id  = 'X1-ZWz1h90xzgg45n_2kpit'
documentation   = 'https://pypi.org/project/pyzillow/'
d2				= 'https://anchetawern.github.io/blog/2014/03/20/getting-started-with-zillow-api/'
zillow_data = ZillowWrapper(web_service_id)


# Test Data
def test_location_data(return_value):
	if returnvalue == 'address':
		return '130 Roswell Commons Way, Roswell, GA 30076'
	elif return_value == 'zipcode':
		return '30076'


# Get Zpids for a specific State / City
list_zpids = m1.get_zpids('Roswell', 'GA')


# Get Deep Search Results
def address_search(address, zipcode, output):
	deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
	result = GetDeepSearchResults(deep_search_response)
	if output == 'sdout':
		print('Home size       => {}'.format(result.home_size))
		print('Property size   => {}'.format(result.property_size))
		print('Home_type       => {}'.format(result.home_type))
		print('Year built      => {}'.format(result.year_built))
		print('Num bedroomes   => {}'.format(result.bedrooms))
		print('Num bathrooms   => {}'.format(result.bathrooms))
		print('Home_sale_price => {}'.format(result.last_sold_price))
		print('Zillow low est  => {}'.format(result.zestimate_valuation_range_high))
		print('Zillow high est => {}'.format(result.zestimate_valuationRange_low))
		print('Value change    => {}'.format(result.zestimate_value_change))
		print('Zillow id       => {}'.format(result.zillow_id))
		print('Zpid            => {}'.format(result.zpid))
	elif output == 'return_id':
		zillow_id = result.zillow_id
		return zillow_id

# Get Updated Property Details
def zillow_id_search(zillow_id):
	updated_property_details_response = zillow_data.\
                                    get_updated_property_details(zillow_id)
	result = GetUpdatedPropertyDetails(updated_property_details_response)
	print('Home type       => {}'.format(result.home_type))
	print('Neighborhood    => {}'.format(result.neighborhood))
	print('School District => {}'.format(result.school_district))
	print('\n')
	
	return None



def run_zillow_id_search_4_list(list_zpids):

	for zpid in list_zpids:
		zpid_str = str(zpid)
		try:
			zillow_id_search(zpid_str)
		except pyzillow.pyzillowerrors.ZillowError as err:
			print(err)



address_search('100 Lakeview Rdg', 30076, 'sdout')
zillow_id_search(65448088)
#print(list_zpids)




