# -*- coding: utf-8 -*-
"""

@author: Jordan


 Joining:
     real estate sales parcels
     Parcel centroids
     State spending summaries


    NOTES: 
        Change criteria of join?? join of all 3 is very limited. 
        
"""

import pandas as pd
import matplotlib.pyplot as plt

#%% Importing Data

# Sales
sales = pd.read_csv('Output/Real Estate/adk_park_munis.csv',
                    dtype = {'print _key':str,'school_code':str})
                    
# Centroid
#### SAMPLE set
centroid_sam = pd.read_csv('Hedonic Analysis/Output/adk_centroids_sample.csv',dtype = {'PRINT_KEY':str})
centroid = centroid_sam
#### Primary set
centroid = pd.read_pickle('Hedonic Analysis/Output/Centroid_parcels_data.zip')

# Tax
################# Select codes & Properties
pclass = 931
prefix = 'adk'
################

classdisct = {931:'532a', 980:'Easments', 940:'Reforested_other',932:'532b',990:'Other'}
taxcode = 'Allclass'

if pclass != 'Allclass': # if pclass is not None, subset based on class code. 
    taxcode = classdisct[pclass]

####
tax = pd.read_excel(f'Output/{taxcode}/{taxcode}_{prefix}_parcel_tax.xlsx',dtype = 
                    {'Print Key Code':str,'School Code':str,'Local SWIS':str})
county = pd.read_excel(f'Output/{taxcode}/{taxcode}_{prefix}_parcel_tax.xlsx', sheet_name = 1)
muni = pd.read_excel(f'Output/{taxcode}/{taxcode}_{prefix}_parcel_tax.xlsx', sheet_name = 2)
school = pd.read_excel(f'Output/{taxcode}/{taxcode}_{prefix}_parcel_tax.xlsx', sheet_name = 3, dtype = {'School Code':str})


##################

#%% Checking Duplicates & Cleaning
non_unique_count = sales['print_key'].duplicated().sum()

# Duplicate Checking
# Print the count of non-unique values
# print("Number of non-unique values in sales 'print_key':", sales['print_key'].duplicated().sum())
# print("Number of non-unique values in centroid 'print_key':", centroid['PRINT_KEY'].duplicated().sum())
# print("Number of non-unique values in tax 'print_key':", tax['Print Key Code'].duplicated().sum())

# Cleaning

# sales
sales['school_code'] = sales['school_code'].str.replace('\.0$', '')




#%% Merging data sets


# Converting columns to string
tax['SWIS'] = tax['SWIS'].astype(str)
tax['Print Key Code'] = tax['Print Key Code'].astype(str)

centroid['SWIS'] = centroid['SWIS'].astype(str)
centroid['PRINT_KEY'] = centroid['PRINT_KEY'].astype(str)

sales['swis_code'] = sales['swis_code'].astype(str)
sales['print_key'] = sales['print_key'].astype(str)
sales['school_code'] = sales['school_code'].astype(str)
sales['county_name'] = sales['county_name'].astype(str)



#%% Sales and Centroid, Left merge
merge_sc = pd.merge(sales,centroid,
                    how = 'left',
                    left_on =['swis_code','print_key'],
                    right_on = ['SWIS','PRINT_KEY'],
                    indicator = True)

print("Number of rows left-only for SC merge:", merge_sc['_merge'].value_counts()['left_only'])
merge_sc = merge_sc.drop('_merge',axis=1)

#%% Joining summary data to sales parcels
## County

merge_sct = pd.merge(merge_sc,
                    county[['County', 'Total County Select Tax Received (k)',
                            'County Real Property Taxes and Assessments (k)', 'County Local Revenues (k)', 
                            'County Total Revenues (k)', '% County Property revenue from select tax', 
                            '% County Local revenue from select tax', '% County Total revenue from select tax']],
                    how='left',
                    left_on=['county_name'],
                    right_on = ['County'],
                    indicator = True)
print("Number of rows left-only for SC County merge:", merge_sct['_merge'].value_counts()['left_only'])
merge_sct = merge_sct.drop('_merge',axis=1)

## Municipality
merge_sct = pd.merge(merge_sct,
                    muni[['Municipality Name', 'Total Municipal Select Tax Received (k)', 'Municipality Real Property Taxes and Assessments (k)', 
                          'Municipality Local Revenues (k)', 'Municipality Total Revenues (k)', '% Municipality Property revenue from select tax', 
                          '% Municipality Local revenue from select tax', '% Municipality Total revenue from select tax']],
                    how='left',
                    left_on=['muni_name'],
                    right_on = ['Municipality Name'],
                    indicator = True)
print("Number of rows left-only for SC Muni merge:", merge_sct['_merge'].value_counts()['left_only'])
merge_sct = merge_sct.drop('_merge',axis=1)
print("Number of unique values in 'Municipality Name':", merge_sct['Municipality Name'].nunique())

## School 
merge_sct = pd.merge(merge_sct,
                    school[['School Code','School District Name', 'Total School Select Tax Received (k)', 'School Real Property Taxes and Assessments (k)', 'School Local Revenues (k)',
                            'School Total Revenues (k)', '% School Property revenue from select tax', '% School Local revenue from select tax',
                            '% School Total revenue from select tax']],
                    how='left',
                    left_on=['school_code'],
                    right_on = ['School Code'],
                    indicator = True)
print("Number of rows left-only for SC School merge:", merge_sct['_merge'].value_counts()['left_only'])
merge_sct = merge_sct.drop('_merge',axis=1)


#%% Merging TC and sales

# many to one sales
# munic_sum['Subdiv FIPS'] = func_parcel_tax.groupby('Municipality Name')['Subdiv FIPS'].first().reset_index(drop=True)

# merge_tcs = pd.merge(merge_tc,sales,
#                       how = 'right',
#                       left_on=['County','Local SWIS','School Code'],
#                       right_on=['county_name','swis_code','school_code'])


# Tax/Centroid and Sales (How many 532a sales within the year)
# merge_tcs_select = pd.merge(merge_tc,sales, # this is local swis
#                                       left_on=['Local SWIS','Print Key Code'],
#                                       right_on=['swis_code','print_key'])


#Dropping un-needed cols
merge_sct = merge_sct.drop(['Unnamed: 0','buyer_last_name2', 'buyer_street_nbr', 'buyer_street_name', 'buyer_city', 'buyer_state',                        
                            'COUNTY_NAME', 'MUNI_NAME', 'PARCEL_ADDR', 'SBL', 'CITYTOWN_NAME', 'LOC_ST_NBR',
                          'LOC_STREET', 'LOC_UNIT', 'LOC_ZIP','FRONT', 'DEPTH', 'SCHOOL_NAME' , 
                          'PRIMARY_OWNER', 'MAIL_ADDR', 'PO_BOX', 'MAIL_CITY', 'MAIL_STATE', 'MAIL_ZIP', 'ADD_OWNER', 'ADD_MAIL_ADDR', 'ADD_MAIL_PO_BOX', 'ADD_MAIL_CITY', 
                          'ADD_MAIL_STATE', 'ADD_MAIL_ZIP', 'BOOK', 'PAGE', 'MUNI_PARCEL_ID', 'SWIS_SBL_ID', 'SWIS_PRINT_KEY_ID', 'SPATIAL_YR', 
                          'OWNER_TYPE', 'NYS_NAME', 'NYS_NAME_SOURCE', 'DUP_GEO', 'ORIG_FID', 
                           
                            'swis_code', 'county_name', 'muni_name', 'muni_type', 'school_code', 'school_name', 'print_key', 
                            'vlg_print_key', 'total_av', 'vlg_total_av', 'seller_last_name', 'seller_first_name', 'buyer_last_name', 'buyer_first_name', 
                            'street_nbr', 'street_name', 'atty_last_name', 'atty_first_name', 'atty_phone', 'swis_county', 'book', 'page', 'deed_date', 'sale_date', 
                            'sale_price', 'personal_prop', 'cod_usable', 'rar_usable', 'front', 'depth',  'nbr_of_parcels', 'prop_class_last_roll',
                            'prop_class_desc_last_roll', 'prop_class_at_sale', 'prop_class_desc_at_sale', 'grid_east', 'grid_north'],
                           
                            axis = 1)
print(merge_sct.columns.tolist())
####################
merge_sct.to_csv(f'Output/{taxcode}/{taxcode}_{prefix}_Hedonic_ana_sct.csv')
###################