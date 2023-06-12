# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:10:35 2023

@author: chris


NOTES:
        
"""

import pandas as pd
import numpy as np

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
merged_hpi = merged_hpi.rename(columns={'County':'county_name', 'Year':'year', 'HPI':'hpi'})
merged_hpi = merged_hpi.set_index(['county_name', 'year'])

hpi_2021 = merged_hpi.xs('2021', level='year')
hpi_2021_mult=merged_hpi/hpi_2021

#%% 

hpi_cat = hpi_cat.drop(columns=['State', 'FIPS code', 'Annual Change (%)', 'HPI with 1990 base', 'HPI with 2000 base'])
hpi_cat['HPI'] = hpi_cat['HPI'].astype(float)
hpi_cat = hpi_cat.rename(columns={'County':'county_name', 'Year':'year', 'HPI':'hpi'})
hpi_cat = hpi_cat.set_index(['county_name', 'year'])

hpi_2021 = hpi_cat.xs('2021', level='year')
hpi_2021_mult=hpi_cat/hpi_2021

#%% Importing csv files. Dwnloaded all real estate transacitons from a 
#   ten year period from counties that contain the Adirondack Park. 

#Manually deleted row 8674 in lewis_14_19.csv due to typo in print key. 

# There is a typo in line 6383 of warren_14_19 source document. street_nbr cell 
# was empty from source material. . This change was updated manually in the csv file. 

# There is a typo in line 6383 of warren_14_19 source document. street_nbr cell 
# was empty from source material. . This change was updated manually in the csv file.

#Deleted lines 6802, 7776 manually due to data quality issue.


adk_county_list = {'clinton' :'09', 'essex':'15', 'frankin':'16', 'fulton':'17', 
            'hamilton':'20', 'herkimer':'21', 'lewis': '23', 'oneida':'30', 
            'st_lawrence':'40', 'saratoga':'41', 'warren':'52', 
            'washington':'53' }

transactions=[]

for name, code in adk_county_list.items():
    current = pd.read_csv(f"Input/Real Estate Transactions/ADK/{code}14_19.csv",index_col=False, dtype=(str))
    transactions.append(current)

adk_county_data_1419 = pd.concat(transactions)

#%% 
transactions=[]

for name, code in adk_county_list.items():
    current = pd.read_csv(f"Input/Real Estate Transactions/ADK/{code}20_CUR.csv",index_col=False, dtype=(str))
    transactions.append(current)

adk_county_data_20cur=pd.concat(transactions)

#Creates a standard date format for sale date transactions. 
adk_county_data_1419['std_date'] = pd.to_datetime(adk_county_data_1419['sale_date'])
adk_county_data_20cur['std_date']= pd.to_datetime(adk_county_data_20cur['sale_date'])

#Creating a sale year column for future HPI multiplier.
adk_county_data_1419['Year'] = adk_county_data_1419['std_date'].dt.year
adk_county_data_20cur['Year'] = adk_county_data_20cur['std_date'].dt.year


#%% Dropping non-relevant columns

drop= ['vlg_print_key', 'vlg_total_av', 'seller_last_name', 'seller_first_name',
       'buyer_last_name', 'buyer_first_name', 'street_nbr', 'street_name', 
       'atty_last_name','atty_first_name', 'atty_phone', 'swis_county', 'book',
       'page', 'deed_date', 'personal_prop', 'cod_usable', 'rar_usable', 
       'front', 'depth', 'total_sale_acres', 'nbr_of_parcels', 'prop_class_last_roll',	
       'prop_class_desc_last_roll', 'grid_east', 'grid_north', 'zip5', 'zip4',
       'buyer_zip5', 'buyer_zip4', 'buyer_last_name2', 'buyer_street_nbr', 
       'buyer_street_name', 'buyer_city', 'part_parcel_flag', 'condo_flag', 
       'contract_date', 'second_swis', 'new_const_flag', 'vlg_rar_usable', 
       'roll_yr','rps_update_flag', 'rps_update_date', 'cor_update_flag', 
       'oth_update_flag', 'last_fm_date', 'rollmatch_flag', 'form_recd', 
       'load_date', 'assessor_reviewed_flag', 'cond_business_sale', 
       'cond_buyer_is_seller', 'cond_company_sale', 'cond_deed_type', 
       'cond_estate', 'cond_govt_sale', 'cond_interest_conv', 'cond_multiple_swis',
       'cond_other', 'cond_relative_sale', 'cond_signif_change', 'cond_memo', 
       'vlg_signif_change_flag']

adk_county_data_1419 = adk_county_data_1419.drop(drop, axis=1)
adk_county_data_20cur = adk_county_data_20cur.drop(drop, axis=1)


#%% Creating a dictionary of municipalities within the park. Source:
    # https://apa.ny.gov/local_government/LGS/ADKTownsVillagesWebsites.pdf
    # Corinth through Tupper Lake are villages. 
adk_muni = ['Altona', 'Arietta', 'AuSable', 'Bellmont', 'Benson', 'Black Brook', 
        'Bleecker', 'Bolton', 'Brighton', 'Broadalbin', 'Caroga', 'Chester', 
        'Chesterfield', 'Clare', 'Clifton', 'Colton', 'Corinth', 'Croghan', 
        'Crown', 'Dannemora', 'Day', 'Diana', 'Dresden', 'Duane', 'Edinburg', 
        'Elizabethtown', 'Ellenburg', 'Ephratah', 'Essex ', 'Fine', 
        'Forestport', 'Fort Ann', 'Franklin', 'Greenfield', 'Greig', 'Hadley', 
        'Hague', 'Harrietstown', 'Hope', 'Hopkinton', 'Horicon', 'Indian Lake',
        'Inlet', 'Jay', 'Johnsburg', 'Johnstown', 'Keene', 'Lake George', 
        'Lake Luzerne', 'Lake Pleasant', 'Lawrence', 'Lewis', 'Long', 
        'Lyonsdale', 'Mayfield', 'Minerva', 'Morehouse', 'Moriah', 'Newcomb', 
        'North', 'North Hudson', 'Northampton', 'Ohio', 'Oppenheim', 
        'Parishville', 'Peru', 'Piercefield', 'Pitcairn', 'Plattsburgh', 
        'Providence', 'Putnam', 'Queensbury', 'Remsen', 'Russia', 'Salisbury',
        'Santa Clara', 'Saranac', 'Schroon', 'St. Armand', 'Stony Creek ', 
        'Stratford', 'Thurman', 'Ticonderoga', 'Tupper Lake',
        # Corinth through Tupper Lake are villages. 
        'Corinth', 'Dannemora', 'Lake George', 'Lake Placid', 'Mayfield', 'Northville', 
        'Saranac Lake', 'Speculator', 'Tupper Lake',
        # End village lsit 
        'Warrensburg', 'Watson', 'Waverly', 'Webb', 'Wells', 'Westport', 
        'Willsboro', 'Wilmington'
        ]

adk_counties = [adk_county_data_1419, adk_county_data_20cur]
#%% Appending datasets together

merged_adk_counties = pd.concat([adk_county_data_1419, adk_county_data_20cur])
#Fixes leading 0 
merged_adk_counties['swis_code'] = merged_adk_counties['swis_code'].str.zfill(6)

merged_adk_counties[['sale_price', 'total_av']] = merged_adk_counties[['sale_price', 'total_av']].astype(float)
merged_adk_counties['print_key'] = merged_adk_counties['print_key'].astype(str)
merged_adk_counties['sale_date'] = pd.to_datetime(merged_adk_counties['sale_date'])
merged_adk_counties['merged_swis_print'] = merged_adk_counties['print_key']+merged_adk_counties['swis_code']

#%% 
trim_dups = merged_adk_counties.dropna(subset=['merged_swis_print'])
is_dup = merged_adk_counties.duplicated(subset=['merged_swis_print'])
duplicate_rows = merged_adk_counties[is_dup]
merged_adk_counties = trim_dups[~is_dup]  
#%% 
#Dropping non-arms length sales baed on arms_length_flag column  
merged_adk_counties = merged_adk_counties[merged_adk_counties['arms_length_flag']=='Y']

# creating two datasets for municipalities that contain the park 
# and non-park municipalities
 
adk_park_munis = merged_adk_counties[merged_adk_counties.muni_name.isin(adk_muni)]
non_adk_park_munis = merged_adk_counties[~merged_adk_counties.muni_name.isin(adk_muni)]
#%% 
adk_park_munis = adk_park_munis.sort_values(['std_date']).drop_duplicates(['merged_swis_print'],keep = 'last')
non_adk_park_munis = non_adk_park_munis.sort_values(['std_date']).drop_duplicates(['merged_swis_print'],keep='last')

adk_park_dups = adk_park_munis.duplicated(subset=['merged_swis_print'], keep=False)
non_adk_park_dups = adk_park_munis.duplicated(subset=['merged_swis_print'], keep=False)

#%% 
merged_adk_counties.to_csv('Output/Real Estate/merged_adk_counties.csv')
adk_park_munis.to_csv('Output/Real Estate/adk_park_munis.csv')
non_adk_park_munis.to_csv('Output/Real Estate/non_adk_park_munis.csv')




#%% Catskill Real Estate Data
cat_county_list = {'delaware':'12', 'greene':'19', 'sullivan':'48', 'ulster':'51'}

#%% 
transactions = []

for name, code in cat_county_list.items():
    current = pd.read_csv(f"Input/Real Estate Transactions/CAT/{code}14_19.csv",index_col=False)
    transactions.append(current)

cat_county_data_1419 = pd.concat(transactions)

#%% 
transactions=[]

for name, code in cat_county_list.items():
    current = pd.read_csv(f"Input/Real Estate Transactions/CAT/{code}20_CUR.csv",index_col=False)
    transactions.append(current)

cat_county_data_20cur=pd.concat(transactions)
#%% 

cat_county_data_1419['std_date'] = pd.to_datetime(cat_county_data_1419['sale_date'])
cat_county_data_20cur['std_date']= pd.to_datetime(cat_county_data_20cur['sale_date'])

cat_county_data_1419['year'] = cat_county_data_1419['std_date'].dt.year
cat_county_data_20cur['year'] = cat_county_data_20cur['std_date'].dt.year

cat_county_data_1419 = cat_county_data_1419.drop(drop, axis=1)
cat_county_data_20cur = cat_county_data_20cur.drop(drop, axis=1)

 
#%% Catskill  municipality and county dictionaries 

cat_muni = [
            'Denning', 'Lexington', 'Colchester', 'Hunter', 'Windham', 'Andes',
            'Neversink','Woodstock','Rockland','Middletown','Rochester','Cairo',
            'Olive','Jewett','Catskill','Hancock','Hurley','Fallsburgh',
            'Mamakating','Rosendale','Fremont','Forestburgh','Davenport','Bethel',
            'Marbletown','Tompkins','Walton','Lumberland','Highland','Thompson'
            'Roxbury','Shandaken','Liberty','Gardiner','Plattekill','Shawangunk',
            'Athens'
            ]

cat_counties = (cat_county_data_1419, cat_county_data_20cur)

#%% 

#######################################
# JE CODE ATTEMPT

merged_cat_counties = pd.concat([cat_county_data_1419,cat_county_data_20cur])

# Formatting columns for join
merged_cat_counties['county_name'] = merged_cat_counties['county_name'].str.lower()

merged_cat_counties['county_name'] = merged_cat_counties['county_name'].astype(str)
merged_cat_counties['year'] = merged_cat_counties['year'].astype(str)
merged_cat_counties['year'] = merged_cat_counties['year'].where(~merged_cat_counties['year'].str.endswith('.0'), merged_cat_counties['year'].str[:-2])

# Setting Index
merged_cat_counties.set_index(['county_name','year'], inplace=True)

# Dropping 2023 and invalid Sales
merged_cat_counties = merged_cat_counties.drop(index='2023', level='year')
merged_cat_counties = merged_cat_counties.drop(index='nan', level='year')

# Merge from index
merged_cat_counties = pd.merge(merged_cat_counties,hpi_2021_mult,
                    how='left',
                    left_index = True,
                    right_index = True,
                    indicator = True)

print("Number of rows left-only for HPI mult merge:", merged_cat_counties['_merge'].value_counts()['left_only'])


# Merge DF for checking
# mergecat_left_only = merged_cat_counties[merged_cat_counties['_merge'] == 'left_only']
# del mergecat_left_only

#%%
#######################################
# Columns not merging correctly hpi, adjusted_amt are listed as nan. 
# merged_cat_counties = pd.concat([cat_county_data_1419,cat_county_data_20cur, hpi_2021_mult])
           
# merged_cat_counties['hpi'] = merged_cat_counties['hpi'].astype(float)

merged_cat_counties['adjusted_amt'] = merged_cat_counties['sale_price']* merged_cat_counties['hpi']

merged_cat_counties['adjusted_amt'] = merged_cat_counties['adjusted_amt'].astype(float)


merged_cat_counties['sale_date'] = pd.to_datetime(merged_cat_counties['sale_date'])

merged_cat_counties['sale_price'] = pd.to_numeric(merged_cat_counties['sale_price'],errors='coerce') 
merged_cat_counties['total_av'] = pd.to_numeric(merged_cat_counties['total_av'],errors='coerce')
merged_cat_counties = merged_cat_counties.dropna(subset=['sale_price', 'total_av'])

merged_cat_counties[['sale_price', 'total_av']] = merged_cat_counties[['sale_price', 'total_av']].astype(int)

#%%  Formating Merged_cat_counties columns

merged_cat_counties['print_key'] = merged_cat_counties['print_key'].astype(str)
merged_cat_counties['swis_code'] = merged_cat_counties['swis_code'].astype(str)
merged_cat_counties['sale_date'] = pd.to_datetime(merged_cat_counties['sale_date'])
merged_cat_counties['merged_swis_print'] = merged_cat_counties['print_key']+merged_cat_counties['swis_code']
#%% Dropping arms length sales

merged_cat_counties = merged_cat_counties[merged_cat_counties['arms_length_flag']=='Y']

cat_park_munis = merged_cat_counties[merged_cat_counties.muni_name.isin(cat_muni)]
non_cat_park_munis = merged_cat_counties[~merged_cat_counties.muni_name.isin(cat_muni)]

#%% 
cat_park_munis = cat_park_munis.sort_values(['sale_date']).drop_duplicates(['merged_swis_print'],keep = 'last')
non_cat_park_munis = non_cat_park_munis.sort_values(['sale_date']).drop_duplicates(['merged_swis_print'],keep='last')

cat_park_dups = cat_park_munis.duplicated(subset=['merged_swis_print'], keep=False)
non_cat_park_dups = cat_park_munis.duplicated(subset=['merged_swis_print'], keep=False)

#%% Dropping real estate sale prices less than 10k. 

merged_adk_counties_10k = merged_adk_counties.drop(merged_adk_counties[(merged_adk_counties['sale_price'] < 10000)].index)
merged_cat_counties_10k = merged_cat_counties.drop(merged_cat_counties[(merged_cat_counties['sale_price'] < 10000)].index)

adk_park_munis_10k = merged_adk_counties_10k[merged_adk_counties_10k.muni_name.isin(adk_muni)]
non_adk_park_munis_10k = merged_adk_counties_10k[~merged_adk_counties_10k.muni_name.isin(adk_muni)]

cat_park_munis_10k = merged_cat_counties_10k[merged_cat_counties_10k.muni_name.isin(cat_muni)]
non_cat_park_munis_10k = merged_cat_counties_10k[~merged_cat_counties_10k.muni_name.isin(cat_muni)]




#%% Saving to csvs
merged_adk_counties_10k.to_csv('Output/Real Estate/merged_adk_counties_10k.csv')
adk_park_munis_10k.to_csv('Output/Real Estate/adk_park_munis_10k.csv')
non_adk_park_munis_10k.to_csv('Output/Real Estate/non_adk_park_munis_10k.csv')

merged_cat_counties_10k.to_csv('Output/Real Estate/merged_cat_counties_10k.csv')
cat_park_munis_10k.to_csv('Output/Real Estate/cat_park_munis_10k.csv')
non_cat_park_munis_10k.to_csv('Output/Real Estate/non_cat_park_munis_10k.csv')

#%% 
#save to csv file
merged_cat_counties.to_csv('Output/Real Estate/merged_cat_counties.csv')
cat_park_munis.to_csv('Output/Real Estate/cat_park_munis.csv')
non_cat_park_munis.to_csv('Output/Real Estate/non_cat_park_munis.csv')

#%% 
#saves to csv file.
merged_adk_counties.to_csv('Output/Real Estate/merged_adk_counties.csv')
adk_park_munis.to_csv('Output/Real Estate/adk_park_munis.csv')
non_adk_park_munis.to_csv('Output/Real Estate/non_adk_park_munis.csv')