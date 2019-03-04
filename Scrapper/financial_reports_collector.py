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
    resp = requests.get(address)
    html_str = resp.text
    soup = BeautifulSoup(html_str, 'html.parser')
    
#     getting filings info info
    table_tag = soup.find('table', class_='tableFile2')
    rows = table_tag.find_all('tr')
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) > 3:
            filing = cells[0].text
            doc_link = 'https://www.sec.gov' + cells[1].a['href']
            filing_date = dt.date.fromisoformat(cells[3].text[0:10])
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
            time.sleep(.1)
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
    
    return filings_df


def filings_collector(cik):
    establishing_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=exclude&start=0&count=100'
    establishing_df = filings_df(establishing_url)
    for i in range(1,10):
        try:
            new_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=exclude&start={i}00&count=100'
            page_df = filings_df(new_url)
            establishing_df = establishing_df.append(page_df, ignore_index=True)
        except:
            break
    return establishing_df




