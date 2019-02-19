import os, csv
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime as dt

def filings_df(address):
#     request
    page_dfs = pd.read_html(address)
    filing_df = pd.DataFrame(page_dfs[2])
    
#     headers collector
    headers = []
    for i in range(0,5):
        headers.append(str(filing_df[i][0]))
        
#     headers cleaner
    filing_df = filing_df.drop(0, axis=0)
    filing_df = filing_df.rename(index=str, columns={0:headers[0], 1:headers[1],
                                                     2:headers[2], 3:headers[3],
                                                     4:headers[4]})
    filing_df = filing_df.reset_index(drop=True)
    
#     description cleaner
    for i in range(0, len(filing_df)):
        filing_desc = filing_df['Description'][i].split()
        filing_pos = len(filing_desc)-6
        filing_number = filing_desc[filing_pos]
        filing_df['Description'][i] = filing_number
        filing_df['Filing Date'][i] = dt.date.fromisoformat(filing_df['Filing Date'][i])     
        
    
    return filing_df



def filings_collector(cik):
    establishing_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=exclude&start=0&count=100'
    establishing_df = filings_df(establishing_url)
    for i in range(1,10):
        try:
            url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=&dateb=&owner=exclude&start={i}00&count=100'
            page_df = filings_df(url)
            establishing_df = establishing_df.append(page_df, ignore_index=True)
            time.sleep(.1)
        except:
            break
    return establishing_df


# ticker = input('what?')

# test = filings_collector(ticker)

# print(test.tail())
