import pandas as pd
import numpy as np
import requests
from cleaner import Cleaner

ticker = input("Please name a stock ticker").upper()
# period_q = input("Annual or Quarter?").lower()


income_annual_address = f"https://quotes.wsj.com/{ticker}/financials/annual/income-statement"

html = requests.get(income_annual_address).content
df_list = pd.read_html(html)
df = df_list[1]

cleaner = Cleaner(df)

new_df = cleaner.clean_dataframe()

print(new_df.head(50)) 