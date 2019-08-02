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


# MYSQL - CLEAR TABLE FUNCTION-----------------------------------------
def clear_table(mydb, decision = 'No'):

    if decision == 'Yes' or decision == 'yes':

        # Delete Addresses Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM ADDRESSES;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'Addresses' table")

        # Delete House Details Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM HOUSE_DETAILS;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'House Details' table")

        # Delete Schools Data
        mycursor = mydb.cursor()
        sql_command = 'DELETE FROM SCHOOLS;'
        mycursor.execute(sql_command)
        mydb.commit()
        print("Data successfully cleared from 'Schools' table\n")

    elif decision == 'No' or decision == 'no':
        # Do Not Delete Table Data
        print('''Data will not be cleared from the Addresses, 
                 House details and Schools tables\n''')

    # Return None
    return None



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
        return bsObj



# ADDRESS INSERT FUNCTION ------------------------------------------------
def sql_insert_function_addresses(mydb, val):
	try:
		#print('Inserting address information into db')
		mycursor = mydb.cursor()
		sql_command = '''
					INSERT IGNORE INTO ADDRESSES (
					street_address, state, zipcode, city, pull_date, url)
                    VALUES(%s, %s, %s, %s, %s, %s)'''

		mycursor.execute(sql_command, val)
		mydb.commit()
		#print('Address information successfully inserted\n')
		return None
	
	except mysql.connector.errors.ProgrammingError as err:
		print('sql insert addresses function generated an error => {}'.format(err))

	except mysql.connector.errors.IntegrityError as err:
		print('sql insert addresses function generated an error => {}'.format(err))


# SCHOOL RANKING INSERT FUNCTION -----------------------------------------
def sql_insert_function_schools(mydb, val, street_address, state, pull_date, url):
	#print('Inserting school ranking data')

	if len(val) < 3:
		print('Less than three school rankings scraped. Returning 0,0,0')
		return [0,0,0]

	# If its not, lets proceed with the insertion. 
	else:
		try:
			mycursor = mydb.cursor()
			sql_command = '''
			INSERT IGNORE INTO SCHOOLS (

                    street_address, state, pull_date,  
                    elementary_school_rating, middle_school_rating, 
                    high_school_rating, url) 
                    
                    VALUES(%s, %s, %s, %s, %s, %s, %s)'''
			val_insert = [street_address ,state, pull_date, 
						  val[0], val[1], val[2], url]
			mycursor.execute(sql_command, val_insert)
			mydb.commit()
			#print('School information successfully inserted\n')

		except mysql.connector.errors.ProgrammingError as err:
			print('sql insert schools function generated an error => {}'.format(err))
			print('sql insert schools function generated an error => {}'.format(err))


# ZILLOW API INSERT FUNCTION --------------------------------------------------
def replace_none_values(val):
	# ** Note that we need to figure out a way to not have this apply to the dates
	# Define new list object
	new_val = []
	if val != None:
		for value in val:
			if value == None or value == 'None':
				new_val.append(0)
			else:
				new_val.append(value)

	return new_val
		

def sql_insert_function_zillow_api_data(mydb, val):
	#print('Inserting zillow home data')
	mycursor = mydb.cursor()
	sql_command = '''
    INSERT IGNORE INTO HOUSE_DETAILS (
        street_address, pull_date, zillow_id, home_type, 
        tax_year, tax_value, year_built, last_sold_date, last_sold_price, 
        home_size, property_size, num_bedrooms, num_bathrooms, 
        zillow_low_est, zillow_high_est, value_change, zillow_percentile)

    VALUES( %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s) 
    '''
	try:
		mycursor.execute(sql_command, replace_none_values(val))
		mydb.commit()
		#print('Zillow home data successfully inserted into db\n')
	except mysql.connector.errors as err:
		print('Zillow insert function geneted an error => {}'.format(err))

	except mysql.connector.errors.IntegrityError as err:
		print('sql insert zillow function generated an error => {}'.format(err))


	return None




def get_list_homes(bsObj):
    '''
    Purpose:  To get the html tags associated with the list of homes for each page. 
    '''
    try:
        photo_cards = bsObj.find('ul', {'class':'photo-cards'})
        list_homes = photo_cards.findAll('li')
        #list_homes = []
        #[list_homes.append(x) for x in li if 'SingleFamilyResidence' in str(x)]    
        return list_homes

    except AttributeError as err:
        print('Attribute error generated from find photo-card request')
        print('Error => {}\n'.format(err))


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

def get_address(clean_house_tag):
	''' The first comma follows the street name and is followed by the city. 
	    therefore, we should be able to split on the comma and take the string
		value in the index = 0 position to be the address'''
	address = clean_house_tag.split(',')[0]
	return address



# GET ZILLOW API RESULTS-----------------------------------------------------
def get_house_data_zillow_api(address, zipcode, pull_date):
	''' Purpose:  Utilizing the zillow api to query data for a single house 
        Input:    Address and zipcode for a single house
        Output:   None.  We will use insert statement within this function'''

	# User feedback
	#print('Accessing Zillow API')
	try:
		# Instantiate connection to zillow database
		web_service_id  = 'X1-ZWz1h90xzgg45n_2kpit'
		documentation   = 'https://pypi.org/project/pyzillow/'
		d2              = 'https://anchetawern.github.io/blog/2014/03/20/getting-started-with-zillow-api/'	
		zillow_data = ZillowWrapper(web_service_id)
	
		# Start Search
		deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
		result = GetDeepSearchResults(deep_search_response)

		# Create Object for the old & new stdout
		old_stdout = sys.stdout
		new_stdout = StringIO()
		sys.stdout = new_stdout

		# Generate stdout - should redirect to StringIO 
		print('Key, Value')
		print('zillow_id,{}'.format(result.zillow_id))
		print('home_type,{}'.format(result.home_type))
		print('tax_year,{}'.format(result.tax_year))
		print('tax_value,{}'.format(result.tax_value))
		print('year_built,{}'.format(result.year_built))
		print('last_sold_date,{}'.format(result.last_sold_date))
		print('last_sold_price,{}'.format(result.last_sold_price))
		print('home_size,{}'.format(result.home_size))
		print('property_size,{}'.format(result.property_size))
		print('num_bedrooms,{}'.format(result.bedrooms))
		print('num_bathrooms,{}'.format(result.bathrooms))
		print('zillow_low_est,{}'.format(result.zestimate_valuationRange_low))	
		print('zillow_high_est,{}'.format(result.zestimate_valuation_range_high))
		print('zillow_value_change,{}'.format(result.zestimate_value_change))
		print('zillow_percentile,{}'.format(result.zestimate_percentile))

		# Convert stdout from StringIO to String    
		new_stdout_str = new_stdout.getvalue()
		test_stdout_str = open('zillow_api_data.csv', 'w')
		test_stdout_str.write(new_stdout_str)
		test_stdout_str.close()

		# Return to old stdout
		sys.stdout = old_stdout

		# Read CSV back in as a pandas dataframe	
		df = pd.read_csv('zillow_api_data.csv')
		df.set_index('Key', inplace=True)

		# Need to convert values from strings to correct input value for db
		val_zillow_api = []

		val_zillow_api.append(address)
		val_zillow_api.append(pull_date)
		val_zillow_api.append(df.iloc[0,0])                 # zillow_id
		val_zillow_api.append(df.iloc[1,0])                 # home type
		val_zillow_api.append(df.iloc[2,0])                 # tax year
		val_zillow_api.append(df.iloc[3,0])                 # tax value
		val_zillow_api.append(df.iloc[4,0])                 # year built
		# Try to append formatted datetime object.  
		try:
			val_zillow_api.append(datetime.strptime(df.iloc[5, 0], '%m/%d/%Y')) # last sold date
		# If None date append the arbitrary date of 01/01/1900
		except ValueError as err:
			print('Zillow api returned the following sold date => {}'.format(df.iloc[5,0]))
			print('Zillow api value error generated:  {}'.format(err))
			val_zillow_api.append(datetime.strptime('01/01/1900', '%m/%d/%Y')) # last sold date
		
		val_zillow_api.append(df.iloc[6,0])                 # last sold price   
		val_zillow_api.append(df.iloc[7,0])                 # home size

		# Test if property value == none.  Appaned 0 if None. 
		if df.iloc[8,0] == None or df.iloc[8,0] == 'None':
			val_zillow_api.append(0)                    # property size
		else:
			val_zillow_api.append(df.iloc[8,0])
	
		# Continue with other values
		val_zillow_api.append(df.iloc[9,0])                 # number bed rooms
		val_zillow_api.append(df.iloc[10,0])                # num bathrooms
		val_zillow_api.append(df.iloc[11,0])                # zillow_low_est
		val_zillow_api.append(df.iloc[12,0])                # zillow high est
		val_zillow_api.append(df.iloc[13,0])                # value change	
		val_zillow_api.append(df.iloc[14,0])                # zillow percentile
	
		# Return List Object to be passed to sql insert function
		#print('Zillow API data successfully obtained\n')
		return val_zillow_api

	except pyzillow.pyzillowerrors.ZillowError:
		print('pyzillow generated an error')

	except ZillowError as err:
		print('Zillow generated an error => {}'.format(err))

# GET URL ---------------------------------------------------------------------

def get_url(home_data):
	if 'url' in str(home_data):
		
		regex_href = re.compile('/homedetails/.+_zpid/"}')
		re_search  = re.search(regex_href, str(home_data))
		href     = re_search.group().split('"')[0]	
		return href



# GET SCHOOL RANKINGS ----------------------------------------------------------

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

    try:
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

