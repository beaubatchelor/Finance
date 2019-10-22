import datetime as dt
from bs4 import BeautifulSoup
import re
import numpy as np
import datetime as dt


def page_scrapper(soup):
	results_list = []
	result_rows = soup.find_all('li', class_='result-row')
	for result in result_rows:
		result_dict = {}
		result_data = result.p
		space_pos = result_data.time['datetime'].index(' ')
		result_dict['Link'] = result_data.a.get('href')
		result_dict['Title'] = result_data.a.text.replace('*','').lower()
		result_dict['Date'] = dt.date.fromisoformat(result_data.time['datetime'][:space_pos])
		try:
			result_dict['Location'] = result_data.find('span', class_ = 'result-hood').text.replace('(','').replace(')','').replace(' ','').lower()
		except:
			result_dict['Location'] = ''
		try:
			result_dict['Price'] = int(result_data.find('span', class_ = 'result-price').text.replace('$',''))
		except:
			continue
		try:
			result_dict['Info'] = result_data.find('span', class_ = 'housing').text.replace(' ','').replace('\n','')
		except:
			continue
		results_list.append(result_dict)

	return results_list

def page_cleaner(results_list):

	for records in results_list:
		records['Bedrooms'] = np.nan
		records['SquareFootage'] = np.nan
		raw_info = records['Info']
		raw_location = records['Location']
		bed_rooms_len = 0
		
		if 'br' in raw_info:
			br_pos = raw_info.index('br')
			bed_rooms = int(raw_info[:br_pos])
			records['Bedrooms'] = bed_rooms
			bed_rooms_len = len(list(str(bed_rooms))) + 3
			
		if 'ft2' in raw_info:
			ft2_pos = raw_info.index('ft2')
			square_footage = int(raw_info[bed_rooms_len:ft2_pos])
			records['SquareFootage'] = square_footage
		
		if np.isnan(records['SquareFootage']):
			pass
		else:
			records['PricePerSqFt'] = records['Price'] / records['SquareFootage']

		if np.isnan(records['Bedrooms']):
			pass
		else:
			records['PricePerRoom'] = records['Price'] / records['Bedrooms']

	return results_list

