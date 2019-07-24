# IMPORT LIBRARY-----------------------------------------------------------------------
import re
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


# IMPORT MODULES----------------------------------------------------------------------
import module1_address_school_data as m1
import module2_zillow_api as m2

# INSTANTIATE CONNECTION TO MYSQL DATABASE--------------------------------------------
mydb = mysql.connector.connect(
                host='localhost',
                user= input('mysql user_name   : '),
                passwd= input('mysql password    : '),
                database= input('mysql database    : '))

# SCRAPE DATA FOR EACH PAGE-----------------------------------------------------------
def main_get_home_data(city, state):
	
	# Create DataFrame Object - Holds Housing Data
	df_home_data = pd.DataFrame({})
	
	# Get bsObj and max page Num
	max_page_num = m1.get_bsObj_main_page(city, state, 1, 'max_page_num')

	# Lists to capture Home Data
	'''to be replaced by insert statements'''

	# Iterate Over Pages_________________________________________________
	'''We iterate over each page, scraping the housing address from the list of houses'''
	for page_num in range(1, max_page_num + 1):
		# User Info
		print('Scraping page {} of {}'.format(page_num, max_page_num))		
		
		# Get Find Tag where house photos are saved on page (list of houses)
		bsObj_other_pages = m1.get_bsObj_main_page(city, state, page_num)
		bsObj = bsObj_other_pages
		
		# Get List of Houses (Photo-cards) for each page)
		list_homes = m1.get_list_homes(bsObj)
		print('Getting list of homes')	

		# Count Number of Homes
		Count_num_pages = 0
	
		# Loop Over tags___________________________________________________
		for home_data in list_homes:
		
			# Try to Mine values from page
			try:
				# Clean tags
				clean_objs = m1.clean_house_tags(home_data)
	
				# Iterate list of data on each house_________________________________
				
				# Scrape the data
				val_location_data = m1.scrape_location_and_school_data(clean_objs, 'location')
				m1.sql_insert_function_addresses(mydb, val_location_data)

				# Insert School Data
				val_schools =		m1.scrape_location_and_school_data(clean_objs, 'school')
				m1.sql_insert_function_schools(mydb, val_schools)

				# Run Zillow API - Get House Details
				Dict_house_data	= m1.scrape_location_and_school_data(clean_objs, 'zillow_api')
				address			= Dict_house_data['street_address']
				zipcode			= Dict_house_data['zipcode']
				val_zillow_api_data = m2.get_house_data_zillow_api(address, zipcode)
				m2.sql_insert_function_home_data(mydb, val_zillow_api_data) 
					
			# Catch Attribute Exception		
			except AttributeError as err:
				pass
		
		# Generate Random Sleep Period
		sleep_seconds = random.randint(1,3)
		Count_num_pages +=1
		print('Data successfully scraped for page {}'.format(Count_num_pages))
		print('Sleeping for {} seconds\n'.format(sleep_seconds))
		sleep(sleep_seconds)		



	# User Feedback 	
	print('Saving results to excel file {}'.format(excel_file_name))
	print('Returning results')
	print(df_home_data)
	
	return None		



# USER INPUT---------------------------------------------------------------------

# User Input Data:
City =  input('Enter City (ex: Roswell): ')
State = input('Enter State (ex: GA)    : ')
'''tables = ADDRESSES, HOUSE_DETAILS, SCHOOLS'''
# Ask if they want to clear th etables
clear_tables_decision = input('''Do you want to clear the followint tables:
	1. Addresses, 
	2. House Details, 
	3. Schools

	Indicate Yes or No:  ''')
m1.clear_table(mydb, clear_tables_decision)


# MAIN FUNCTION----------------------------------------------------------------

main_get_home_data(City, State)












