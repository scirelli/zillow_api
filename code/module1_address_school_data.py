import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib
from time import sleep
from datetime import datetime
import random


# MYSQL INSERT FUNCTIONS ----------------------------------------------

def sql_insert_function_addresses(mydb, val):
        mycursor = mydb.cursor()
        sql_command = '''
		INSERT INTO ADDRESSES (
					
					street_address, state, zipcode, city, longitude, 
					latitude, pull_date, url) 
					
					VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'''
        
		mycursor.execute(sql_command, val)
        mydb.commit()
        return None

def sql_insert_function_schools(mydb, val):
        mycursor = mydb.cursor()
        sql_command = '''
		INSERT INTO SCHOOLS (

					street_address, state, pull_date,  
					elementary_school_rating, middle_school_rating, 
					high_school_rating, url) 
					
					VALUES(%s, %s, %s, %s, %s, %s, %s)'''

        mycursor.execute(sql_command, val)
        mydb.commit()
        return None



# GET MAX PAGE NUMBER --------------------------------------------------
def get_max_page_num(bsObj):
	'''
	Purpose:	Get the max page number from the main page
	Input:		The bsObj from the main page. 
	Output:		Int value of last page'''

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



# GET ADDRESSES OF ALL PROPERTIES IN CITY/STATE COMBO-----------------------

def get_bsObj_main_page(city, state, page, return_value = None):
	'''
	Purpose:	Obtain the bsObj for the main page where the list of houses are located. 
	Input:		Seach criteria includes the city and state where the house is located
				The purpose of the page input is to iterate each of the pages to scrape
				more housing data. 
	**Note:		We should expand the search criteria to include other limiting fields. 
	Output:		The user may chose to output the max page number from the page
				or return the bsObj of the page	'''
	# Define url object
	url = 'https://www.zillow.com/homes/for_sale/{}-{}/{}_p/'\
				       .format(city, state, page)
	
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
	
	# Chose Output
	if return_value == 'max_page_num':
		max_page_num = int(get_max_page_num(bsObj))
		return max_page_num
	else:
		# Return Tuple Object bsObj + max_page
		return bsObj		


# GET TAGS ASSOCIATED WITH LIST OF HOMES DISPLAYED ON EACH PAGE
def get_list_homes(bsObj):
	'''
	Purpose:  To get the html tags associated with the list of homes for each page. 
	'''
	try:
		photo_cards = bsObj.find('ul', {'class':'photo-cards'})
        list_homes = photo_cards.findAll('li')
        return list_homes

	except AttributeError as err:
		print('Attribute error generated from find photo-card request')
        print('Error => {}\n'.format(err))


# CLEAN TAGS CONTAINING INDIVIDUAL HOUSE DATA

def clean_house_tags(home_data):
	'''Input:	Individual tag for containing home data
	   Output:  list of clean data represented by key:value pairs. 
	   Purpose: We obtain the content associated with each house, 
                convert it to a bsObj text and clean it of punctuation. 
                the structure of the data looks like a dict obj with key:value
                pairs.  Therefore, we split the string on the : and mine the list
                for the values. 
	'''
	# Drill down into tag attributes 'script', 'contents'
	tag_contents = home_data.script.contents    
	# Split string on comma to separate data into key_value pairs
	create_list = tag_contents[0].split(',')	
	# Clean list by replacing punctuation
	clean_objs = [x.replace('"', '').replace('{', '')\
                   .replace('}', '').replace('@', '') for x in create_list] 

	# Return clean string
	return clean_objs


# FUNCTION TO GET MAX PAGE NUMBER FROM START PAGE------------------------------
def get_school_ranking(url):
	url_full = 'https://www.zillow.com' + url
	print(url_full)
	Content = urllib.request.Request(url_full, headers={
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
	
	# Narrow down tags to the ones that hold the ratings
	school_list = bsObj.findAll('div', {'class':'ds-nearby-schools-list'})	
	try:
		print('School list => {}'.format(school_list))
		ratings = school_list[0].findAll('div', {'class':'ds-school-rating'})
		# Create a list to house the ratings
		list_ratings = []
		# Iterate the trags retreiving the text from each, then split to get just the rating
		[list_ratings.append(int(x.text.split('/')[0])) for x in ratings]	
		# Return a list object with the ratings
		return list_ratings
	except IndexError as err:
		print('School ratings function generated an errr => {}'.format(err))
		print('Returning school rankings = [0,0,0]\n')
		return [0,0,0]


# CREATE DICTIONARY OBJECT OF SCRAPED DATA-------------------------------------

def scrape_housing_data(obj):
	'''Input:	String object that contains key:value pairs of housing data
	   Output:	Dictionary object containing this data'''
	
	# Split Key Value Pairs on colon so that we may reference the key
	key_value = obj.split(':')

	# Create Dictionary Object to House Scraped Data
    Dict_house_data = {}

	# Define Pull Date
    Dict_house_data['pull_date']    = datetime.today().date() #2019-07-23

	# Address
	elif key_value[0]   == 'streetAddress':
		Dict_house_data['street_address']           = key_value[1]
	# State
	elif key_value[0]   == 'addressRegion':
		Dict_house_data['state']                    = key_value[1]
	# Zip Code
	elif key_value[0] == 'postalCode':
		Dict_house_data['zipcode']                  = key_value[1]
	# City
	elif key_value[0] == 'addressLocality':
		Dict_house_data['city']                     = key_value[1]
	# Longitude
	elif key_value[0] == 'longitude':
		Dict_house_data['longitude']                = key_value[1]
	# Latitude
	elif key_value[0] == 'latitude':
		Dict_house_data['latitude']                 = key_value[1]

	# Get Url
	elif key_value[0] == 'url':
		Dict_house_data['url']      = key_value[1]

		# School Ranking Data
		school_rankings = get_school_ranking(url)
        Dict_house_data['elementary_school_rating'] = school_rankings[0]
        Dict_house_data['middle_school_rating']     = school_rankings[1]
        Dict_house_data['high_school_rating']       = school_rankings[2]    

	# Return Dictionary Object
	return Dict_house_data











