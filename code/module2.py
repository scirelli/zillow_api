import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib


urlp1 = 'https://www.zillow.com/homes/for_sale/Roswell-GA/rp/'
urlp2 = 'https://www.zillow.com/homes/for_sale/Roswell-GA/2_p/'
page_numbers = 'ol class:zsg-pagination'


def get_zpids(city, state):
	'''Input:  City must be in format 'Roswell'
		       State must be in format 'GA'
	'''
    # Create list obj to capture zpids
	list_zpids = []

	# Define url object
	page = 1
	url_p1 = 'https://www.zillow.com/homes/for_sale/{}-{}/rp/'.format(city, state)
	url_p2 = 'https://www.zillow.com/homes/for_sale/{}-{}/{}_p/'.format(city, state, page)

	# Define Regex Statement to search for
	'this reject finds all combinations of zpid_ and any length of numbers'
	regex_exp = re.compile('streetAddress.*, ')

	# Generate the url request with zillow headings
	content = urllib.request.Request(url_p1, headers={
                       'authority': 'www.zillow.com',
                       'method': 'GET',
                       'path': '/homes/',
                       'scheme': 'https',
                       'user-agent':
                       ''''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
                        AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/61.0.3163.100 Safari/537.36'''})

	# Home Data Dataframe
	df_home_data = pd.DataFrame({})

	# Open Url
	html = urlopen(content)
	# Create Beautifulsoup object
	bsObj = BeautifulSoup(html.read(), 'lxml')
	# Find Tag where house photos are saved on page (list of houses)
	photo_cards = bsObj.find('ul', {'class':'photo-cards'})
	list_homes = photo_cards.findAll('li')

	# Lists to capture Home Data
	hometype        = []
	street_address  = []
	state           = []
	zipcode         = []
	city            = []
	longitude       = []
	latitude        = []


	# Loop Over tags
	for home_data in list_homes:
		
		# Try Get Content		
		try:
			tag_contents = home_data.script.contents
			
			create_list = tag_contents[0].split(',')
			clean_objs = [x.replace('"', '').replace('{', '')\
				     .replace('}', '').replace('@', '') for x in create_list]

			# Objain values from cleaned subtag
			for obj in clean_objs:
				key_value = obj.split(':')
				# Home Type
				if key_value[0] == 'type':
					hometype.append(key_value[1])
				# Address
				elif key_value[0] == 'streetAddress':
					street_address.append(key_value[1])
				# State
				elif key_value[0] == 'addressRegion':
					state.append(key_value[1])
				# Zip Code
				elif key_value[0] == 'postalCode':
					zipcode.append(key_value[1])
				# City
				elif key_value[0] == 'addressLocality':
					city.append(key_value[1])
				# Longitude
				elif key_value[0] == 'longitude':
					longitude.append(key_value[1])
				# Latitude
				elif key_value[0] == 'latitude':
					latitude.append(key_value[1])
	
		except AttributeError as err:
			pass

	# Build DataFrame
	df_home_data['hometype']		= hometype
	df_home_data['street_address']	= street_address		
	df_home_data['state']			= state
	df_home_data['zipcode']			= zipcode		
	df_home_data['city']			= city
	df_home_data['longitude']		= longitude
	df_home_data['latitude']		= latitude
	
	print(df_home_data)
	
	return None		






get_zpids('Roswell', 'GA')
