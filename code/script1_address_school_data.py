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
import module1_sql_functions as m1
import module2_get_value_functions as m2
import module3_zillow_api as m3
import module4_url_filters as m4


# USER INPUT-------------------------------------------------------------------------
user_name = input('user name:  ')
password  = input('password :  ')
mysql_db  = 'HOUSING_DATA'#input('database :  ')

# INSTANTIATE CONNECTION TO MYSQL DATABASE--------------------------------------------
mydb = mysql.connector.connect(
                host='localhost',
                user= user_name,
                passwd= password,
                database= mysql_db)


# DEFINE PULL DATE-------------------------------------------------------------------
pull_date = datetime.today().date()


# URL SYNTAX FOR FILTERS------------------------------------------------------------



# SCRAPE DATA FOR EACH PAGE-----------------------------------------------------------
def main_get_home_data(city, state):
	
	# Create DataFrame Object - Holds Housing Data
	df_home_data = pd.DataFrame({})
	
	# Get bsObj and max page Num
	max_page_num = m2.get_bsObj_main_page(city, state, 1, 'max_page_num')

	# Lists to capture Home Data
	'''to be replaced by insert statements'''

	# Iterate Over Pages_________________________________________________
	'''We iterate over each page, scraping the housing address from the list of houses'''
	for page_num in range(1, max_page_num + 1):
		
		# User Info
		print('Scraping page {} of {} --------------------------------------------------------'\
				.format(page_num, max_page_num))		
		pull_date = datetime.today().date()
		
		# Get Tags where house photos are saved on page (list of houses)
		bsObj = m2.get_bsObj_main_page(city, state, page_num)
		
		# Get List of Houses (Photo-cards) for each page)
		list_homes = m2.get_list_homes(bsObj)
		
		
		# Page Counts
		Count_num_pages = 1
		count_homes_scraped = 0
		
		#LOOP OVER HOME TAGS________________________________________________________________
		
		if list_homes != None:
			for home in list_homes:
			
				# Asking price
				asking_price = m2.get_sale_asking_price(home)				
	
				# Num home object
				total_homes_on_page = len(list_homes)

				# Clean house tags
				clean_house_tags = m2.clean_house_tags_4_address_zipcode_scrape(home)
				# Can return none object.  pass if None. 
				if clean_house_tags == None:
					pass

				# Otherwise, start scraping data
				else:
					# ADDRESSES TABLE--------------------------------------------------
					'street_address, state, zipcode, city, pull_date, url'
					# Get Url	
					url = m2.get_url(home)
					# Obtain Zipcode
					zip_code	= m2.get_zip_code(clean_house_tags)
					# Obtain Address
					address		= m2.get_address(clean_house_tags)
					# Insert Data Into Database
					val_addresses = [address, state, zip_code, city, pull_date, url]
					m1.sql_insert_function_addresses(mydb, val_addresses)
				
					# ZILLOW API---------------------------------------------------------
					val_zillow_api_data = m3.get_house_data_zillow_api(address, zip_code, 
											 pull_date, asking_price)
					m1.sql_insert_function_zillow_api_data(mydb, val_zillow_api_data)

					# SCHOOL RANKINGS----------------------------------------------------
					school_rankings = m2.get_school_ranking(url)
					m1.sql_insert_function_schools(	mydb, school_rankings, address,  
												pull_date, url)

					# Increment Num homes
					print('{} of {} home data scraped'.format(
						count_homes_scraped, total_homes_on_page))
					count_homes_scraped +=1	
				

			# Generate Random Sleep Period
			print('Data successfully scraped for page {}'.format(page_num))
			sleep_seconds = random.randint(5,10)
			print('Sleeping for {} seconds\n'.format(sleep_seconds))
			sleep(sleep_seconds)		

	return None		


# USER INPUT---------------------------------------------------------------------


# Clear Existing Table Data:
#clear_tables_decision = input('''Do you want to delete the data from the following tables?
#	1. Addresses, 
#	2. House Details, 
#	3. Schools
#	Indicate Yes or No:  ''')
#m1.clear_table(mydb, clear_tables_decision)


# MAIN FUNCTION----------------------------------------------------------------

# Define Run-Type:
run_type = input('Run scraper for an individual city or all? (write: indv or all)' )


# If Individual - Input City/State
if run_type == 'indv':
	# User Input Data:
	City =  input('Enter City (ex: Roswell): ')
	State = input('Enter State (ex: GA)    : ')

	# Run Scraper for Selected City/State
	#main_get_home_data(City, State)

elif run_tupe == 'all':
	df_cities = list(m1.get_ga_muni_data(mydb)['NAME'])
	
	for city in df_cities:
		main_get_home_data(city, 'GA')
		print('Scraping data for city => {}'.format())
else:
	print('Input value incorrect.  Needs to be either "indv or all"')


# NOTES_ ----------------------------------------------------------------------
'''Add filter for home types'''










