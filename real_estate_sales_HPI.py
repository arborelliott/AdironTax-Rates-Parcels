# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 10:47:41 2023

@author: chris
"""

import pandas as pd
#%% Importing county housing price index document from 
# https://www.fhfa.gov/DataTools/Downloads/Pages/House-Price-Index-Datasets.aspx

hpi = pd.read_csv('Input/Real Estate Transactions/HPI_AT_BDL_county.csv',dtype = str)
hpi['County'] = hpi['County'].str.lower()
hpi['County'] = hpi['County'].str.replace('St Lawrence', 'st_lawrence')


adk_county_list = ['clinton', 'essex', 'frankin', 'fulton', 'hamilton', 
                  'herkimer', 'lewis', 'oneida', 'st_lawrence', 'saratoga', 
                  'warren', 'washington' ]

cat_county_list = ['delaware', 'greene', 'sullivan', 'ulster']

hpi = hpi.drop(hpi[~(hpi['State']=='NY')].index)

hpi_adk = hpi[hpi.County.isin(adk_county_list)]
hpi_cat = hpi[hpi.County.isin(cat_county_list)]

merged_hpi = pd.concat([hpi_adk, hpi_cat])
#%% Creating a HPI column for reference year 2021

merged_hpi = merged_hpi.drop(columns=['State', 'FIPS code', 'Annual Change (%)', 'HPI with 1990 base', 'HPI with 2000 base'])


merged_hpi['HPI'] = merged_hpi['HPI'].astype(float)
merged_hpi = merged_hpi.set_index(['County', 'Year'])

hpi_2021 = merged_hpi.xs('2021', level='Year')
hpi_2021_mult=merged_hpi/hpi_2021

#%% 

############# Brought this code into Hedonic_tax_centorid_sales_merge Script for merging



