
'''
This program uses selenium and beautifulsoup to scrape fast food prices in different States for restaurants recorded on https://www.fastfoodmenuprices.com/all-restaurants/. The output is a dataframe where each column shows the date at which the price was recorded and the rows shows the item listed in the menu. The rows are organized by multiple index: restaurant names and location by State. So far, there is only one column of data, collected July 19th 2018.
'''

# load packages
from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.options import Options
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

# function to read in tables in html to a dataframe
'''
input: table element written in html
output: pd.DataFrame object
'''
def parse_html_table(table):
  n_columns = 0
  n_rows=0
  column_names = []

  # Find number of rows and columns
  # we also find the column titles if we can
  for row in table.find_all('tr'):

    # Determine the number of rows in the table
    td_tags = row.find_all('td')
    if len(td_tags) > 0:
      n_rows+=1
      if n_columns == 0:
        # Set the number of columns for our table
        n_columns = 3

  df = pd.DataFrame(columns = range(n_columns), index= range(0,n_rows))
  row_marker = 0
  for row in table.find_all('tr'):
    column_marker = 0
    columns = row.find_all('td')
    for column in columns:
      df.iat[row_marker,column_marker] = column.get_text()
      column_marker += 1
    if len(columns) > 0:
      row_marker += 1

  # Convert to float if possible
  for col in df:
    try:
      df[col] = df[col].astype(float)
    except ValueError:
      pass

  return df.dropna()

# create empty dataframe for the final result
result = pd.DataFrame()

# set up webdriver
chop = webdriver.ChromeOptions()
chop.add_extension('AdBlock_v3.32.0.crx')
browser = webdriver.Chrome(chrome_options = chop)
# scrap html for the first page with all restaurants
path = 'https://www.fastfoodmenuprices.com/all-restaurants/'
page = requests.get(path)
soup = BeautifulSoup(page.content, 'html.parser')
entry_content = soup.find(attrs = {'class':'entry-content'})
links = entry_content.findAll(attrs = {"id": re.compile("^menu-item-\w")})

# create empty lists for restaurant name and data
restaurant_dfs = []
restaurant_labels = []
test_dict = {}

# loops through individual restaurant pages
for link in links:
  restaurant = link.find('a').get('href')
  restaurant_name = link.find('a').get_text()
  print('now on ' + restaurant_name + ' page')
  # selenium to handle dropdown menu
  browser.get(restaurant)
  print('finished loading the page')
  dropdown = Select(browser.find_element_by_class_name('tp-variation'))
  print('found dropdown')
  options = dropdown.options # all options available for the dropdown
  print('found all options in the dropdown')

  # create empty lists for state name and their price data
  dfs = []
  df_labels = []

  # loops through individual states
  for index in range(0,5):
    print('now on option ' + str(index))
    dropdown.select_by_index(index)
    print('selected the option')
    restaurant_state_soup = BeautifulSoup(browser.page_source, 'html.parser')
    print('parsed html')
    restaurant_state_menu = restaurant_state_soup.find('table')
    print('found table')
    # adds the data tables from each state to the empty list
    dfs.append(parse_html_table(restaurant_state_menu))
    test_df = parse_html_table(restaurant_state_menu)
    test_dict[options[index].text] = test_df
    print('parsed and added html table')
    df_labels.append(options[index].text)

  # combines data tables from each state into one table and adds state name as index
  df = pd.concat(dfs, keys = df_labels)

  # write a csv file for each restaurant
  # df.to_csv(restaurant_name + '.csv')
  # print('wrote csv for ' + restaurant_name)
  # solved slow loading problem

  # adds the data tables from each restaurant to the empty list
  restaurant_dfs.append(df)
  restaurant_labels.append(restaurant_name)

# combines data tables from each restaurant into final result and adds restaurant name as another index
result = pd.concat(restaurant_dfs, keys = restaurant_labels)
