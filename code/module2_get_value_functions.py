import re
import sys
from io import StringIO
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
from time import sleep


# GET MAX PAGE NUMBER -------------------------------------------------
def get_max_page_num(bsObj):
    '''
    Purpose:    Get the max page number from the main page
    Input:      The bsObj from the main page. 
    Output:     Int value of last page'''

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


# GET BEAUTIFUL SOUP OBJECT OF PAGE OR TOTAL NUMBER OF PAGES TO SCRAPE--------------
def get_bsObj_main_page(city, state, page, return_value = None):
    '''
    Purpose:    Obtain the bsObj for the main page where the list of houses are located. 
    Input:      Seach criteria includes the city and state where the house is located
                The purpose of the page input is to iterate each of the pages to scrape
                more housing data. 
    **Note:     We should expand the search criteria to include other limiting fields. 
    Output:     The user may chose to output the max page number from the page
                or return the bsObj of the page '''
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
        return (bsObj, url)



# GET LIST OF HOMES --------------------------------------------------
def get_list_homes(bsObj):
	'''
	Purpose:  To get the html tags associated with the list of homes for each page. 
	'''
	url = bsObj[1]
	bsObj = bsObj[0]

	try:
		photo_cards = bsObj.find('ul', {'class':'photo-cards'})
		list_homes = photo_cards.findAll('li')
		return list_homes
	
	except AttributeError as err:
		print('Attribute error generated from find photo-card request')
		print('Sleeping for 30 seconds')
		sleep(30)
		print('Url that generated the error => {}'.format(url))
		print('Error => {}\n'.format(err))
		print('Trying a different approach to retreiving the tag')
	
		try:
			photo_cards = bsObj.find('ul', {'class':'photo-cards photo-cards_wow'})
			list_homes = photo_cards.findAll('li')
			return list_homes
		except AttributeError as err:
			print('Unable to retreive the photocard tag')
			pass
	 


# GET ZIP CODE----------------------------------------------------------
def clean_house_tags_4_address_zipcode_scrape(home_data):
    # Limit to specific tags contianing this phrase
	if '<li><script type="application/ld+json">' in str(home_data):
		home_data    = str(home_data)
		regex        = re.compile('name.*","floor')
		re_search    = re.search(regex, home_data)
		re_group     = re_search.group()
		remove_front = re_group.split(':')[1]
		remove_back  = remove_front.split('floor')[0]
		remove_punct = remove_back.replace('"', '')
		# return clean tag containing address & zipcode	
		return remove_punct

def get_zip_code(clean_house_tag):
	# Search for zipcode    
	regex_zip_code = re.compile('[0-9]{5},')
	re_search_zip  = re.search(regex_zip_code, clean_house_tag)
	re_group_zip   = re_search_zip.group()
	zip_code       = re_group_zip.split(',')[0]
	# Return Zip Code
	return zip_code

# GET ADDRESS ----------------------------------------------------------
def get_address(clean_house_tag):
	''' The first comma follows the street name and is followed by the city. 
	    therefore, we should be able to split on the comma and take the string
		value in the index = 0 position to be the address'''
	address = clean_house_tag.split(',')[0]
	return address



# GET URL ---------------------------------------------------------------------
def get_url(home_data):
	if 'url' in str(home_data):
		
		regex_href = re.compile('/homedetails/.+_zpid/"}')
		re_search  = re.search(regex_href, str(home_data))
		href     = re_search.group().split('"')[0]	
		return href



# GET SCHOOL RANKINGS ----------------------------------------------------------
def get_school_ranking_backup(url):
	url_full = 'https://www.zillow.com' + url

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
	# List of ratings
	list_ratings = []

	try:
		ratings = school_list[0].findAll('div', {'class':'ds-school-rating'})
		# Iterate the trags retreiving the text from each, then split to get just the rating
		[list_ratings.append(int(x.text.split('/')[0])) for x in ratings]   
		# Return a list object with the ratings
		return list_ratings
	except IndexError as err:
		print('Alternative technique generated an error')
		return [0,0,0]
	except ValueError as err:
		print('Alternative technique generated an error')
		return [0,0,0]	

def get_school_ranking(url):
	url_full = 'https://www.zillow.com' + url

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
	# List of ratings
	list_ratings = []

	try:
		ratings = school_list[0].findAll('div', {'class':'ds-school-rating'})
		# Iterate the trags retreiving the text from each, then split to get just the rating
		[list_ratings.append(int(x.text.split('/')[0])) for x in ratings]   
		# Return a list object with the ratings
		return list_ratings

	except IndexError as err:
		print('School list => {}'.format(school_list))
		print('School ratings function generated an error => {}'.format(err))
		print('Url that generated the error => {}'.format(url_full))
		print('Trying a different technique')
		try:
			list_ratings = get_school_ranking_backup(url)
			return list_ratings
	
		except AttributeError as err:
			print('Unable to obtain school rankings. Returning school rankings = [0,0,0]\n')
			return [0,0,0]

	except ValueError as err:
		print('Get school ranking function generated and error => {}'.format(err))
		print('Returning 0,0,0')
		return [0,0,0]		



# GET ASKING PRICE-------------------------------------------------------------------
def get_sale_asking_price(home):
	'''	Purpose:	Get the asking price for the house from the photo tag
		Input:		The input value is the individual home tag 
				This function sits within the "for home in list_homes" loop. 
		Output:		Integer value for asking price'''
	# Test if we can find the article tag
	try:
		test = home.find('article')
		# If this tag is not none, lets try to get the a tag within which sits the list price
		if test != None:
			article = test.a
			list_price = article.find('div', {'class':'list-card-price'})\
						.text.replace('$','').replace(',','')
			# Return asking price as an integer
			return int(list_price)

    # Except an attribute error where no tag is found
	except AttributeError as err:
		print('Get asking price generated an error => {}'.format(err))
		print('Returning asking price => ${}'.format('0'))
		return 0
	
	# Except ValueError - some values look like this 'Est. 166283'
	except ValueError as err:
		print('Get asking price generated an error => {}'.format(err))
		print('Try removing text in asking price')
		try:
			list_price_new = list_price.replace('Est.','').replace('+','').replace('++','')\
									   .replace('--','')
			if list_price_new != None:
				print('Asking price scraped successfully')
				return int(list_price)
			else:
				print('Unable to obtain asking price.  Returning $0')
				return 0
			
		except ValueError as err:
			print('Unable to clean asking price.  Returning $0')
			return 0

		












# TEST GET BSOJB & GET LIST OF HOMES
'''
test_url = '/homedetails/130-Roswell-Commons-Way-Roswell-GA-30076/14669487_zpid/'
print(get_school_ranking(test_url))
'''



