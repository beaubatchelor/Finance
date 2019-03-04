from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime as dt
import requests
import xml.etree.ElementTree as ET



def filings_df(address):
#     variables 
    reports_list = []
    doc_link = ''
    
#     request
    soup = BeautifulSoup(address, 'html.parser')
    
#     getting filings info info
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 3:
            filing = cells[0].text
            doc_link = 'https://www.sec.gov' + cells[1].a['href']
            filing_date = dt.date.fromisoformat(cells[3].text)
            entry = {'filings' : filing, 'doc_link' : doc_link, 'date' : filing_date}
            reports_list.append(entry)
    
#     getting the XBRL link
    for report in reports_list:
        doc_link = report['doc_link']
        doc_resp = requests.get(doc_link)
        doc_str = doc_resp.text
        soup = BeautifulSoup(doc_str, 'html.parser')
        try:
            table_tag = soup.find('table', class_='tableFile', summary='Data Files')
            rows = table_tag.find_all('tr')
            time.sleep(.01)
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 3:
                    if 'INS' in cells[3].text:
                        xbrl_link = 'https://www.sec.gov' + cells[2].a['href']
                        report.update({'xbrl_link' : xbrl_link})
        except:
            report.update({'xbrl_link' : 'N/A'})
        
#     make dataframe
    
    filings_df = pd.DataFrame(reports_list)
    
    return filing_df