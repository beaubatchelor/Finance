import pandas as pd
import numpy as np
import requests

ticker = input("Please name a stock ticker").upper()
# period_q = input("Annual or Quarter?").lower()


income_annual_address = f"https://quotes.wsj.com/{ticker}/financials/annual/income-statement"
balance_annual_address = f"https://quotes.wsj.com/{ticker}/financials/annual/balance-sheet"
cash_annual_address = f"https://quotes.wsj.com/{ticker}/financials/annual/cash-flow"


html = requests.get(income_annual_address).content
df_list = pd.read_html(html)
df = df_list[1]

##finding first column name to rename-
headers = [df.columns.values]
header = headers[0][0]

##finding by 'Thousands' or 'Millions'-
ending = header[48:58]
ending = ending.replace('.','')
ending = ending.replace(' ','')
ending = str(ending)

##formating and droping NAs
df = df.rename(columns={header:'Labels'})
header1 = headers[0][1]
header2 = headers[0][2]
header3 = headers[0][3]
header4 = headers[0][4]
header5 = headers[0][5]
df = df[['Labels',header1,header2,header3,header4,header5]]
income = df.dropna()
income = income.set_index('Labels')

##Deleting rows with %s
income['percentage'] = ''
income['percentage'][income[header1].str.contains('%')] = 'percentage'
income['percentage'][income[header2].str.contains('%')] = 'percentage'
income = income[income['percentage'] != 'percentage']
income = income.drop(['percentage'],axis=1)

income[header1][income[header1].str.contains('-')] = "0"
income[header2][income[header2].str.contains('-')] = "0"
income[header3][income[header3].str.contains('-')] = "0"
income[header4][income[header4].str.contains('-')] = "0"
income[header5][income[header5].str.contains('-')] = "0"

income[header1] = income[header1].str.replace('\(', '-')
income[header1] = income[header1].str.replace('\)', '')
income[header2] = income[header2].str.replace('\(', '-')
income[header2] = income[header2].str.replace('\)', '')
income[header3] = income[header3].str.replace('\(', '-')
income[header3] = income[header3].str.replace('\)', '')
income[header4] = income[header4].str.replace('\(', '-')
income[header4] = income[header4].str.replace('\)', '')
income[header5] = income[header5].str.replace('\(', '-')
income[header5] = income[header5].str.replace('\)', '')

income[header1] = income[header1].str.replace('\,', '')
income[header2] = income[header2].str.replace('\,', '')
income[header3] = income[header3].str.replace('\,', '')
income[header4] = income[header4].str.replace('\,', '')
income[header5] = income[header5].str.replace('\,', '')

print(income.head(50))