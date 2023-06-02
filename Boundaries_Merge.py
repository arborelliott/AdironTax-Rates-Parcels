# -*- coding: utf-8 -*-
"""
@author: Jordan

1. Run First
    This script combines boundary data from 2 seperate data sets (town and city) and (villages) Combined the data set has all three. 
    The main purpose is to match NY SWIS codes to Census FIPS Codes
    This Script outputs NYS_Tax_rates_Levy_Roll21.csv which contains data on tax rates throughout the state, 
    which is used for the next script Parcel_tax_Merge_func.py
    
    INPUT: 
        1. NYS_Civil_Boundaries_TOWN_CITY.csv
        2. NYS_Civil_Boundaries_VILLAGES.csv - Civil boundary data from NYS GIS
        3. Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv - Historical Tax rate data for NYS
    
    OUTPUT: 
        NYS_Tax_rates_Levy_Roll21.csv - Tax rates for 2021, With SWIS and FIPS codes
    
    VARIABLES:
        - Year of tax rates (default 2021)
        
NOTES: 
    
    
"""

import pandas as pd
import matplotlib.pyplot as plt

#%% Importing CSVs
town_city_raw = pd.read_csv('Input/NYS_Civil_Boundaries_TOWN_CITY.csv')
town_city = town_city_raw
villages_raw = pd.read_csv('Input/NYS_Civil_Boundaries_VILLAGES.csv')
villages = villages_raw

#%% Aligning two DFs

#print(villages.columns.tolist())

# Remove unneeded cols
drop = ['MUNITYCODE','OBJECTID']
town_city = town_city.drop(drop, axis = 1)
drop = ['Shape__Area','Shape__Length','OBJECTID']
villages = villages.drop(drop, axis = 1)

# Add muni type col
villages.insert(1, 'MUNI_TYPE', 'village')

# Edit Villages name column
villages['NAME'] = villages['NAME'] + ' village'

# add empty Town Col
town_city.insert(2, 'Town', '')

#%% Concat DFs

tcv = pd.concat([town_city, villages], ignore_index=True)

#%% Parsing FIPS Code

tcv['FIPS_CODE'] = tcv['FIPS_CODE'].astype(str)
tcv.insert(7, 'State FIPS', tcv['FIPS_CODE'].str[:2])
tcv.insert(8, 'County FIPS', tcv['FIPS_CODE'].str[2:5])
tcv.insert(9, 'Subdiv FIPS', tcv['FIPS_CODE'].str[5:10])
tcv.insert(10, 'Place FIPS', tcv['FIPS_CODE'].str[10:])


#tcv.to_csv('NYS_Town_City_Village_Merged.csv', index=False)

#%% Import and format tax levy data

levy_raw = pd.read_csv('Input/Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv')
levy_raw.insert(4,'Village','')
levy_raw.insert(17,'Village Tax Rate (per $1000 value)','')    
levy = levy_raw

levy.rename(columns={
    'County Name': 'County',
    'School Code': 'School Code',
    'Swis Code': 'SWIS'
}, inplace=True)


# Subset of only 2021 data
levy = levy[levy['Roll Year'] == 2021]


# Fix St lawrence naming
levy['County'] = levy['County'].replace('St. Lawrence', 'St Lawrence')
levy = levy.drop(['County Tax Rate Inside Village (per $1000 value)','Municipal Tax Rate Inside Village (per $1000 value)'], axis = 1)


levy.to_csv('Input/Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004_VILLAGE.csv', index = False)

### Append villages data

#%% Merge tax levy Data with boundaries, SWIS to FIPS

#both_tcv = 
merged_tcv = levy.merge(tcv, on='SWIS', how='left', indicator=True)

# Filter out the rows that failed to merge
failed_to_merge = merged_tcv[merged_tcv['_merge'] == 'left_only']

# removing un-needed cols
print(merged_tcv.columns.tolist())
drop = ['Type of Value on which Tax Rates are applied','GNIS_ID','DOS_LL', 'DOSLL_DATE', 'MAP_SYMBOL','DATEMOD','COUNTY','NAME']
merged_tcv = merged_tcv.drop(drop, axis = 1)

# Export to CSV
merged_tcv.to_csv('Input/NYS_Tax_rates_Levy_Roll21.csv', index = False)
