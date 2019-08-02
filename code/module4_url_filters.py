

'''
state = input('state (ex: GA):  ')
city  = input('city  (ex: Woodstock):  ')
root_url = 'https://www.zillow.com/homes/{},-{}_rb/'.format(city, state)
'''

def search_filters(root_url, city, state):
	
	add_filters = input('Do you want to add filters to the search (yes/no)? ')


	if add_filters == 'Yes' or add_filters == 'yes': 
		pre_foreclosures = input('exclude pre-forclosures (yes/no)?  ')
		foreclosures     = input('exclude foreclosures (yes/no)?  ')
		new_construction = input('exclude new-construction (yes/no)?  ')
		auctions		 = input('exclude auctions (yes/no)?  ')
			

		if pre_foreclosures == 'yes':
			root_url = root_url + ',' + '"isPreMarketForeclosure":{"value":false},"isPreMarketPreForeclosure":{"value":false}}'	
		elif foreclosures		== 'yes':
			root_url = root_url + ',' + '"isForSaleForeclosure":{"value":false}}'
		elif new_construction == 'yes':
			root_url = root_url + ',' + '"isNewConstruction":{"value":false}}'
		elif auctions			== 'yes':
			root_url = root_url + ',' + '"Auction":{"value":false}}'
		elif pre_foreclosures or foreclosures or new_construction or auctions == 'yes':
			root_url = root_url + ',' + '"isListVisible":true}' 

		return root_url

	else:
		print('returning root url w/ city state selection')
		return root_url



# Run Function
'''root_url_with_filters = search_filters(root_url, city, state)'''



