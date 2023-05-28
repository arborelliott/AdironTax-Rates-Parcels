# -*- coding: utf-8 -*-
"""
@author: Jordan

This should be run before parcel_tax_merge_func.py
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

#%% Import tax levy data

levy_raw = pd.read_csv('Input/Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv')
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

#%% Merge tax levy Data with boundaries, SWIS to FIPS

merged = levy.merge(tcv, on='SWIS', how='left', indicator=True)

# Filter out the rows that failed to merge
failed_to_merge = merged[merged['_merge'] == 'left_only']

# removing un-needed cols
print(merged.columns.tolist())
drop = ['Type of Value on which Tax Rates are applied','GNIS_ID','DOS_LL', 'DOSLL_DATE', 'MAP_SYMBOL','DATEMOD','COUNTY','NAME']
merged = merged.drop(drop, axis = 1)

# Export to CSV
merged.to_csv('Input/NYS_Tax_rates_Levy_Roll21.csv', index = False)
