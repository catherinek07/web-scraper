# Imports

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import schedule
import time
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file('/Users/catherinekim/Downloads/web-scraper-390713-24a7f17c336f.json', scopes=scopes)

gc = gspread.authorize(credentials)

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

# open a google sheet
gs = gc.open_by_url('https://docs.google.com/spreadsheets/d/1xuFjF6sTgE40wcYu5cnbsOnD9riV-ENaDTsKAi_iiac/edit#gid=0')
# select a work sheet from its name
worksheet1 = gs.worksheet('Sheet1')

# Initialize driver path
driver_path = '/Users/catherinekim/Downloads/chromedriver_mac64/chromedriver'


# Define csv function
def scrape_and_save():
    # Browser setup
    browser = webdriver.Chrome(executable_path=driver_path)
    url = 'https://www.rolimons.com/marketactivity'
    browser.get(url)
    browser.refresh()

    # Search for sales and timestamps
    timestamp = browser.find_elements(By.CLASS_NAME, "activity_entry_timestamp")
    sale_price = browser.find_elements(By.CLASS_NAME, "pl-1")

    # Creating arrays and inserting elements
    timestamp_list = []
    sales_price_list = []

    for time in timestamp:
        timestamp_list.append(time.text)
    for price in sale_price:
        sales_price_list.append(price.text)

    # Unique identifier created by concatenating each item's timestamp and price
    id_list = []
    for i in range(len(timestamp_list)):
        id_list.append(str(timestamp_list[i]) + str(sales_price_list[i]))

    # Append into data
    df = pd.DataFrame({'Timestamp': timestamp_list, 'Sale Price': sales_price_list, 'ID': id_list})

    #df.to_csv('market_activity.csv', mode='a', index=False, header=False)
    #print(df)

    df_values = df.values.tolist()
    gs.values_append('Sheet1', {'valueInputOption': 'RAW'}, {'values': df_values})
    browser.close()



# Run function
scrape_and_save()

# Schedule to run csv update function every X minutes
schedule.every(15).minutes.do(scrape_and_save)


# Continue running function
while True:
    schedule.run_pending()
    time.sleep(1)
