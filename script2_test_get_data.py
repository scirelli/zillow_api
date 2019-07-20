import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib







urlp1 = 'https://www.zillow.com/homes/for_sale/Roswell-GA/rp/'
urlp2 = 'https://www.zillow.com/homes/for_sale/Roswell-GA/2_p/'
page_numbers = 'ol class:zsg-pagination'

def test_regex():
    test_statement = 'today the 18th of July is a good day to code'
    regex_exp = re.compile('\d+')
    regex_search = re.search(regex_exp, test_statement)
    regex_result = regex_search.group()


def get_zpid(url):

    list_zpids = []


    regex_exp = re.compile('zpid_\d+')
    content = urllib.request.Request(url, headers={
                       'authority': 'www.zillow.com',
                       'method': 'GET',
                       'path': '/homes/',
                       'scheme': 'https',
                       'user-agent':
                       ''''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)
                        AppleWebKit/537.36 (KHTML, like Gecko)
                        Chrome/61.0.3163.100 Safari/537.36'''})
    html = urlopen(content)
    bsObj = BeautifulSoup(html.read(), 'lxml')
    tag1 = bsObj.findAll('ul', {'class':'photo-cards'})
    for x in tag1:
        li = x.find_all('li')
        for x in li:
            regex_search = re.search(regex_exp, str(x))
            try:
                result = regex_search.group()
                print('Resutl => {}'.format(result))
                list_zpids.append(result.split('zpid_')[1])
            except AttributeError as err:
                pass

    print(list_zpids)


get_zpid(urlp1)




