
import pyzillow
from pyzillow.pyzillow import ZillowWrapper, GetDeepSearchResults, GetUpdatedPropertyDetails 


user_name       = 'ccirelli2'
pswd            = 'Work4starr'
web_service_id  = 'X1-ZWz1h90xzgg45n_2kpit'
documentation   = 'https://pypi.org/project/pyzillow/'


address = '1175 Lea Drive, Roswell, GA'
zipcode = '30076'
zillow_data = ZillowWrapper(web_service_id)


# Get Deep Search Results
deep_search_response = zillow_data.get_deep_search_results(address, zipcode)
result = GetDeepSearchResults(deep_search_response)
print('Home size       => {}'.format(result.home_size))
print('Property size   => {}'.format(result.property_size))
print('Home_type       => {}'.format(result.home_type))
print('Year built      => {}'.format(result.year_built))
print('Num bedroomes   => {}'.format(result.bedrooms))
print('Num bathrooms   => {}'.format(result.bathrooms))
print('Home_sale_price => {}'.format(result.last_sold_price))
print('Zillow low est  => {}'.format(result.zestimate_valuation_range_high))
print('Zillow high est => {}'.format(result.zestimate_valuationRange_low))
print('Value change    => {}'.format(result.zestimate_value_change))
zillow_id = result.zillow_id


# Get Updated Property Details 
updated_property_details_response = zillow_data.get_updated_property_details(zillow_id)
result2 = GetUpdatedPropertyDetails(updated_property_details_response)
print('Neighborhood    => {}'.format(result2.neighborhood))
print('School District => {}'.format(result2.school_district))

