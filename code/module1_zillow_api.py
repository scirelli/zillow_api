import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib
from time import sleep
from datetime import datetime

# FUNCTION TO GET MAX PAGE NUMBER FROM START PAGE

def get_max_page_num(bsObj):

	# Find Tag where house photos are saved on page (list of houses)
	links_pages = str(bsObj.find('ol', {'class':'zsg-pagination'}))
	# Search for pages
	regex = re.compile('Page [0-9]+')
	re_search = re.findall(regex, links_pages)
	last_page = re_search[-1]	
	
	# Get Number of last page
	regex_page_num = re.compile('[0-9]+')
	re_search      = re.search(regex_page_num, last_page)
	last_page_num  = re_search.group()
	
	# Return last page number
	return last_page_num


# GET ADDRESSES OF ALL PROPERTIES IN CITY/STATE COMBO
def get_bsObj_main_page(city, state, page):
	'''
		***Note that this is the input for the next function get_home_data***
		Input:  City must be in format 'Roswell'
		       State must be in format 'GA'
	'''
	# Define url object
	url = 'https://www.zillow.com/homes/for_sale/{}-{}/{}_p/'\
				       .format(city, state, page)

	# Define Regex Statement to search for
	'this reject finds all combinations of zpid_ and any length of numbers'
	regex_exp = re.compile('streetAddress.*, ')

	# Generate the url request with zillow headings
	Content = urllib.request.Request(url, headers={
                       'authority': 'www.zillow.com',
                       'method': 'GET',
                       'path': '/homes/',
                       'scheme': 'https',
                       'user-agent':
                       ''''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
                        AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/61.0.3163.100 Safari/537.36'''})
	html = urlopen(Content)
	# Create Beautifulsoup object
	bsObj = BeautifulSoup(html.read(), 'lxml')
	max_page_num = get_max_page_num(bsObj)
	# Return Tuple Object bsObj + max_page
	return (bsObj, max_page_num)		


# SCRAPE DATA FOR EACH PAGE
def get_home_data(city, state):
	
	# Home Data Dataframe
	df_home_data = pd.DataFrame({})
	
	# Get bsObj and max page Num
	bsObj_main = get_bsObj_main_page('Roswell', 'GA', 1)
	max_page_num = int(bsObj_main[1])

	# Lists to capture Home Data
	hometype        = []
	street_address  = []
	state           = []
	zipcode         = []
	city            = []
	longitude       = []
	latitude        = []

	# Iterate Over Pages
	for page_num in range(1, max_page_num + 1):
		# User Info
		print('Scraping page {} of {}'.format(page_num, max_page_num))		

		# Find Tag where house photos are saved on page (list of houses)
		bsObj_other_pages = get_bsObj_main_page('Roswell', 'GA', page_num)
		bsObj = bsObj_other_pages[0]
		photo_cards = bsObj.find('ul', {'class':'photo-cards'})
		list_homes = photo_cards.findAll('li')

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
			
			# Catch Attribute Exception		
			except AttributeError as err:
				pass
		
		# User Feedback & Sleep
		sleep_seconds = 3
		print('Data successfully scraped')
		print('Sleeping for {} seconds\n'.format(sleep_seconds))
		sleep(sleep_seconds)		

	# Build DataFrame
	df_home_data['hometype']		= hometype
	df_home_data['street_address']	= street_address		
	df_home_data['state']			= state
	df_home_data['zipcode']			= zipcode		
	df_home_data['city']			= city
	df_home_data['longitude']		= longitude
	df_home_data['latitude']		= latitude

	# Generate Results & Excel File	
	date = datetime.today().date()
	excel_file_name  = 'zillow_scraper_output_{}.xlsx'.format(date)
	df_home_data.to_excel(excel_file_name)
	print('Saving results to excel file {}'.format(excel_file_name))
	print('Returning results')
	print(df_home_data)
	
	return None		


# RUN FUNCTION
get_home_data('Roswell', 'GA')



