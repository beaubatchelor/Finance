import pandas as pd
import numpy as np
import requests
from datetime import datetime as dt
from datetime import timedelta as td
from cleaner import Cleaner
from pymongo import MongoClient

#Variables
date_threshold = 30

# set up mongo client
client = MongoClient('localhost', 27017)
db = client.financial_db
collection = db.wsj_statements_collection


ticker = input("Please name a stock ticker").upper().lstrip().rstrip()
statement = input("Please name a statement (income statement, balance sheet, or cash flow)").lower().lstrip().rstrip().replace(" ","-").replace("_","-")
period = input("Annual or Quarter?").lower().lstrip().rstrip()

address = f"https://quotes.wsj.com/{ticker}/financials/{period}/{statement}"

def date_differance_threshold(date_string, days_threshold_int):
    days_threshold_int = int(days_threshold_int)
    dt_date = dt.strptime(date_string, '%m/%d/%Y').date()
    past_threshold = True
    
    if dt_date < dt.utcnow().date() - td(days=days_threshold_int):
        past_threshold = True
    else:
        past_threshold = False
        
    return past_threshold

try:
    doc = collection.find_one({"company_id" : f"{ticker}_{statement}_{period}"})
except:
    doc = {"company_id" : "", "last_update" : "0/0/0000"}


if doc["company_id"] != f"{ticker}_{statement}_{period}" or date_differance_threshold(doc["last_update"], date_threshold) == True:
    try:
        # testing address / finding table
        html = requests.get(address).content
        df_list = pd.read_html(html)
        df = df_list[1]
        
        #cleaning table
        cleaner = Cleaner(df)
        new_df = cleaner.clean_dataframe()
        
        #df to dict
        new_df_dict = new_df.to_dict()        

        # Creating a new Dict
        now = f'{dt.utcnow().date().month}/{dt.utcnow().date().day}/{dt.utcnow().date().year}'
        company_info_dict = {}
        company_info_dict["company_id"] = f"{ticker}_{statement}_{period}"
        company_info_dict["last_update"] = now
        company_info_dict['data'] = new_df_dict
        collection.insert_one(company_info_dict)
        
    except:
        print(f"Sorry, nothing found for Ticker: {ticker}, Statement: {statement}, and Period: {period}")
else:
    print(doc)