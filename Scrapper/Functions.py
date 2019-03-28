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
    time.sleep(.1)
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
            for row in rows:
                cells = row.find_all('td')
                if len(cells) > 3:
                    if 'INS' in cells[3].text or 'INSTANCE' in cells[1].text:
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
            new_url = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=&dateb=&owner=exclude&start={i}00&count=100'
            page_df = filings_df(new_url)
            establishing_df = establishing_df.append(page_df, ignore_index=True)
        except:
            break
    return establishing_df

def xbrl_dict(xbrl_address):
#     response and ElementTree
    xbrl_resp = requests.get(xbrl_address)
    time.sleep(.1)
    xbrl_str = xbrl_resp.text
    root = ET.fromstring(xbrl_str)
    
#     defining namespace prefixes
    uri_dict = {}
    for child in root:
        uri_pos = child.tag.index('}')
        uri = ''.join(child.tag[1:uri_pos])
        
        try:
            both_exist = uri_dict['sec'] + uri_dict['gaap']
            break
        except:
            both_exist = ''

        if uri[0:23] == 'http://xbrl.sec.gov/dei':
            uri_dict['sec'] = uri
        elif uri[0:18] == 'http://xbrl.us/dei':
            uri_dict['sec'] = uri
        elif uri[0:23] == 'http://fasb.org/us-gaap':
            uri_dict['gaap'] = uri
        elif uri[0:22] == 'http://xbrl.us/us-gaap':
            uri_dict['gaap'] = uri
    
##     defining xbrl data dictionary
#       collecting standard file info
    doc_date_str = root.find('sec:DocumentPeriodEndDate', uri_dict).text
    fisc_year_end = root.find('sec:CurrentFiscalYearEndDate', uri_dict).text
    fisc_year_end_suffix = fisc_year_end[-5:len(fisc_year_end)]
    doc_date_suffix = doc_date_str[-5:len(doc_date_str)]
    doc_date_dt = dt.datetime.fromisoformat(doc_date_str)
    exceptions = 1
    
    if doc_date_suffix == fisc_year_end_suffix:
        doc_fisc_year = doc_date_dt.year-1    
    
    if uri_dict['sec'][0:23] == 'http://xbrl.sec.gov/dei':
        entry_dict = {'company_name' : root.find('sec:EntityRegistrantName', uri_dict).text,
                    'CIK' : root.find('sec:EntityCentralIndexKey', uri_dict).text,
                    'doc_date' : doc_date_dt,
                    'doc_year' : root.find('sec:DocumentFiscalYearFocus', uri_dict).text,
                    'doc_period' : root.find('sec:DocumentFiscalPeriodFocus', uri_dict).text,
                    'common_shares_outstanding' : int(root.find('sec:EntityCommonStockSharesOutstanding', uri_dict).text),
                    'amendment_flag' : root.find('sec:AmendmentFlag', uri_dict).text}
        
    elif uri_dict['sec'][0:18] == 'http://xbrl.us/dei':
#         entry_dict = {'company_name' : root.find('sec:EntityRegistrantName', uri_dict).text,
#                     'CIK' : root.find('sec:EntityCentralIndexKey', uri_dict).text,
#                     'doc_date' : doc_date_dt,
#                     'doc_year' : doc_fisc_year,
#                     'doc_period' : root.find('sec:DocumentType', uri_dict).text[-1],
#                     'common_shares_outstanding' : int(root.find('sec:EntityCommonStockSharesOutstanding', uri_dict).text),
#                     'amendment_flag' : root.find('sec:AmendmentFlag', uri_dict).text}
        entry_dict = {'company_name' : 'previouse xbrl version'}
    
    
#     Collecting dynamic file information
    for child in root:
        if entry_dict['company_name'] == 'previouse xbrl version':
            break
        else:
            uri_pos = child.tag.index('}')
            uri = ''.join(child.tag[1:uri_pos])
            name = ''.join(child.tag[int(uri_pos+1):len(child.tag)])
            current_focus_period = entry_dict['doc_period']
            current_focus_year = entry_dict['doc_year']

        #     Quater or Annual
            if current_focus_period == "Q2" or current_focus_period == "Q3":
                current_context = str(f'{current_focus_year}{current_focus_period}QTD')
            elif current_focus_period == "Q1":
                current_context = str(f'{current_focus_year}{current_focus_period}YTD')
            elif current_focus_period[0] == "F" or current_focus_period[0] == "K":
                current_context = str(f'{current_focus_year}Q4YTD')  

        #     Finding only current info
            if uri == uri_dict['gaap']:
                context_ref = child.attrib['contextRef']
                if len(context_ref) == 11:
                    if context_ref[2:12] == current_context:
                        try:
                            decimals = int(child.attrib['decimals'])
                            if decimals <= 0:
                                data = int(child.text)
                            else:
                                data = float(child.text)   
                            entry_dict[name] = data    
                        except:
                            exceptions += 1

                    elif len(context_ref) == 8:
                        if context_ref[2:8] == current_context[0:6]:
                            try:
                                decimals = int(child.attrib['decimals'])
                                if decimals <= 0:
                                    data = int(child.text)
                                else:
                                    data = float(child.text)
                                entry_dict[name] = data
                            except:
                                exceptions += 1
    entry_dict['exceptions'] = exceptions            
                            
    return entry_dict
