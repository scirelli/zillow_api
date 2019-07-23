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

# IMPORT MODULES----------------------------------------------------------------------
import module1_address_school_data as m1


# INSTANTIATE CONNECTION TO MYSQL DATABASE--------------------------------------------
mydb = mysql.connector.connect(
                host='localhost',
                user= input('user_name   : '),
                passwd= input('password  : '),
                database= input('Database: '))

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

		# Count Number of Homes
		Count_num_homes = 0
	
		# Loop Over tags___________________________________________________
		for home_data in list_homes:
		
			# Try to Mine values from page
			try:
				# Clean tags
				clean_objs = m1.clean_house_tags(home_data)
	
				# Iterate list of data on each house_________________________________
				for obj in clean_objs:
					# Scrape the data
					dict_h_data = m1.scrape_housing_data(obj)
					
					# Insert Address Data
					val_addresses = [
									dict_h_data['street_address'], dict_h_data['state'], 
									dict_h_data['zipcode'], dict_h_data['city'], 
									dict_h_data['longitude'], dict_h_data['latitude'], 
									dict_h_data['pull_date'], dict_h_data['url']
									]
					m2.sql_insert_function_addresses(mydb, val_addresses)

					# Insert School Data
					val_schools =  [
									dict_h_data['street_address'], dict_h_data['state'], 
									dict_h_data['pull_date'], 
									dict_h_data['elementary_school_rating'],
									dict_h_data['middle_school_rating'], 
									dict_h_data['high_school_rating'], dict_h_data['url']
								   ] 
					
					# Increase Count Num Homes
					Count_num_homes += 1

	
			# Catch Attribute Exception		
			except AttributeError as err:
				pass
		
		# Generate Random Sleep Period
		sleep_seconds = random.randint(1,3)
		print('Data successfully scraped')
		print('Sleeping for {} seconds\n'.format(sleep_seconds))
		sleep(sleep_seconds)		



	# User Feedback 	
	print('Saving results to excel file {}'.format(excel_file_name))
	print('Returning results')
	print(df_home_data)
	
	return None		



get_home_data('woodstock', 'ga')

