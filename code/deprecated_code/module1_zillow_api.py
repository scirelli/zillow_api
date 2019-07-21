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
	regex_exp = re.compile('zpid_\d+')

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
	# Open Url
	html = urlopen(content)
	# Create Beautifulsoup object
	bsObj = BeautifulSoup(html.read(), 'lxml')
	# Find Tag where house photos are saved on page (list of houses)
	tag1 = bsObj.findAll('ul', {'class':'photo-cards'})
	for x in tag1:
	# Find all li tags
		li = x.find_all('li')
		for x in li:
			# Within this result search for all zpids
			regex_search = re.search(regex_exp, str(x))
			try:
				# Try returning the results
				result = regex_search.group()
				print('Resutl => {}'.format(result))
				# Append zpids to our list object
				list_zpids.append(result.split('zpid_')[1])
			# Except searches where no zpid is found. 
			except AttributeError as err:
				pass

	# Return Info:
	print('{} zpids have been scraped for city = {} and state = {}'\
			.format(len(list_zpids), city, state))

	# Return list of zpids
	return list_zpids






