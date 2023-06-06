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
### need all code parcels?

### Select codes & Properties
tax = pd.read_excel('Output/Allclass/Allclass_all_parcel_tax.xlsx',dtype = 
                    {'Print Key Code':str,'School Code':str,'Local SWIS':str})



#%% Checking Duplicates & Cleaning
non_unique_count = sales['print_key'].duplicated().sum()

# Duplicate Checking
# Print the count of non-unique values
print("Number of non-unique values in sales 'print_key':", sales['print_key'].duplicated().sum())
print("Number of non-unique values in centroid 'print_key':", centroid['PRINT_KEY'].duplicated().sum())
print("Number of non-unique values in tax 'print_key':", tax['Print Key Code'].duplicated().sum())

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

# Tax and Centroid
merge_tc = pd.merge(tax, centroid,
                                      left_on=['SWIS','Print Key Code'],
                                      right_on=['SWIS','PRINT_KEY'],
                                      indicator=True)
# many to one sales
# merge_tcs = pd.merge(merge_tc,sales,
#                      how = 'right',
#                      left_on=['County','Local SWIS','School Code'],
#                      right_on=['county_name','swis_code','school_code'])


# Tax/Centroid and Sales (How many 532a sales within the year)
merge_tcs_select = pd.merge(merge_tc,sales, # this is local swis
                                      left_on=['Local SWIS','Print Key Code'],
                                      right_on=['swis_code','print_key'])


# Dropping un-needed cols
for df in [tax,centroid,sales]:
    print(df.columns.tolist())
    print()

merge_tcs = merge_tcs.drop(['Unnamed: 0_x',
                            
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
