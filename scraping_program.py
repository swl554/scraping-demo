
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
                n_columns = len(td_tags) + 100

    if n_rows > 5:
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

        return df.dropna(axis = 1, how = 'all')
def collect_dropdown_tables(link, i):

    dfs = []
    df_labels = []

    browser.get(link)
    parsed_page = BeautifulSoup(requests.get(link).content, 'html.parser')
    html_dropdown = parsed_page.find('select')
    try:
        dropdown = Select(browser.find_element_by_class_name(html_dropdown['class']))
    except:
        dropdown = Select(browser.find_element_by_id(html_dropdown['id']))

    dropdown_options = dropdown.options
    for index in range(0, len(dropdown_options)):
        dropdown.select_by_index(index)
        table = BeautifulSoup(browser.page_source, 'html.parser').find('table')
        if table != None:
            dfs.append(parse_html_table(table))
            df_labels.append(dropdown_options[index].text)

    try:
        df = pd.concat(dfs, keys = df_labels)
        output_data[link_names[i]] = df
    except ValueError:
        print('no data')
def collect_tables(link, i):

    parsed_page = BeautifulSoup(requests.get(links[i]).content, 'html.parser')
    tables = parsed_page.findAll('table')

    if tables != None:
        for table in tables:
            try:
                table_name = table['id']
            except:
                table_name = 'no table id'
            output_data[table_name] = parse_html_table(table)
    else:
        print('no table')
def process_links(links):

    for i in range(0,len(links)):
        print(f'Currently on {links[i]}.')
        try:
            parsed_page = BeautifulSoup(requests.get(links[i]).content, 'html.parser')
            print('parsed page')
            html_dropdown = parsed_page.find('select')
            if html_dropdown != None:
                print('dropdown found')
                collect_dropdown_tables(links[i], i)
            else:
                print('dropdown not found')
                try:
                    collect_tables(links[i], i)
                except ValueError:
                    pass

            a_elements = parsed_page.findAll('a')
            if a_elements != None:
                print('more links found')
                for a_element in a_elements:
                    link = a_element.get('href')
                    link_name = a_element.get_text()
                    if link not in links or opened_links:
                        links.append(link)
                        link_names.append(link_name)

        except:
            print('invalid url')


        links.remove(links[i])
        link_names.remove(link_names[i])
        #opened_links.append(links[i])
        #opened_link_names.append(link_names[i])
        print(f'number of output data: {len(output_data)}')

# set up webdriver
chop = webdriver.ChromeOptions()
chop.add_extension('AdBlock_v3.32.0.crx')
browser = webdriver.Chrome(chrome_options = chop)

links = []
link_names = []
opened_links = []
opened_link_names = []
output_data = {}

#start_page = 'https://www.eia.gov/'
start_page_name = 'U.S. Energy Information Administration'
#start_page = 'https://www.ncdc.noaa.gov/ghcn/comparative-climatic-data'
#start_page = 'https://finance.yahoo.com/quote/FDA.F/history/'
start_page = 'https://www.nass.usda.gov/Charts_and_Maps/Agricultural_Prices/pricecn.php'
#start_page = 'https://www.nass.usda.gov/Statistics_by_State/Florida/index.php'

links.append(start_page)
link_names.append(start_page_name)

process_links(links)
process_links(links)

print(f'opened links: {opened_links}')
print(f'output data: {output_data}')
