# -*- coding: utf-8 -*-
"""
@author: Jordan

2. Run after Boundaries_merge.py
    This script runs a function which retrieves information from the Census API 
    based on desired geographic regions within NY.

    INPUT: None
    OUTPUT: Census information is exported to Output/Census/... to be used in later scripts
    VARIABLES: retrieve_census(for_clause, title)
    choose the geographic location desired in the census, and the title you want to be attached to the outputs. 

NOTES: 
    #census spatial join
    sub parts of counties  map?
    

"""

import pandas as pd
import matplotlib.pyplot as plt
import requests


#%% IMPORTING DATA FROM API AND FORMATING

# Set variable api to the American Community Survey 5-Year API endpoint for 2018 as shown below:
api = 'http://api.census.gov/data/2020/acs/acs5'


def retrieve_census(for_clause, title):
    
    #for_clause = ''
    #title = ''
    
    in_clause = 'state:36'
    key_value = '98f45bb20730399804c81c734eb32ca2b92dd188' # census API key
    
    payload = {
        'get':"NAME,B20002_001E,B01003_001E,B20003_001E,B02001_001E,B02001_002E,COUNTY,GEO_ID",
        'for':for_clause,
        'in':in_clause,
        'key':key_value
        }
    
    # The call will build an HTTPS query string, send it to the API endpoint, and collect the response
    response = requests.get(api, payload)
    
    if response.status_code == 200:
        print('\nAPI Success')
        print(response.url)
    else:
        print('\nAPI Failure',response.status_code)
        print(response.text)
        assert False # stops script if statement is reached
    
    #%% Formattting data received from API
    
    
    row_list = response.json()
    colnames = row_list[0]
    datarows = row_list[1:]
    
    census = pd.DataFrame(columns = colnames, data = datarows)
    
    # Formatting data received
    
    #census['GEOID'] = census['state']+census['county']
    
    #   income
    census['median (k)'] = census['B20002_001E'].astype(float)/1000 # expressing census in thousands
    census['aggregate (k)'] = census['B20003_001E'].astype(float)/1000
    
    #   populations
    census['total Pop'] = census['B01003_001E']
    
    #   race
    census['total race'] = pd.to_numeric(census['B02001_001E'], errors='coerce')
    census['white alone'] = pd.to_numeric(census['B02001_002E'], errors='coerce')
    census['other race'] = census['total race'] - census['white alone']
    
    #   education?
    
    ## drop original census columns 
    census = census.drop(['B20002_001E','B20003_001E','B01003_001E','B02001_001E','B02001_002E'], axis=1)
    
    
    with pd.ExcelWriter(f'Output/Census/{title}_Census.xlsx',date_format=None, mode='w') as writer:
        census.to_excel(writer, sheet_name = f'{title}_Census')

#Choose geo locations
 #county
 #school district (unified)
 #place
 
 #retrieve_census(for_clause, title):
     
retrieve_census('place:*','Place')
retrieve_census('county:*','County')
retrieve_census('school district (unified):*','School')
retrieve_census('county subdivision:*','subdiv')

#%% Merging Census data with Municipal Info

#Boundaries = pd.read_csv('New_York_State_Municipal_Civil_Boundaries.csv')