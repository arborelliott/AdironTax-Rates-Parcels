# -*- coding: utf-8 -*-
"""

@author: Jordan

This script joins the village level tax rates with the parcel data in order to calculate the amount of tax received by ADK villages
for 532a parcels. 

"""

import pandas as pd
import matplotlib.pyplot as plt

tax = pd.read_csv('Input/Village_Property_Taxrates_2021.csv')
parcel = pd.read_csv('Input/Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv')


#%% Cleaning

def remove_nancol(df):
    # Find columns with all NaN values
    nan_columns = df.columns[df.isnull().all()]

    # Remove columns with all NaN values
    df = df.drop(nan_columns, axis=1)

    return df

tax = remove_nancol(tax)
parcel = remove_nancol(parcel)

tax.rename(columns={
    'County Name': 'County',
    'School Code': 'School Code',
    'Swis Code': 'SWIS',
}, inplace=True)

parcel.rename(columns={
    'County Name': 'County',
    'SWIS Code': 'Local SWIS',
    'Municipality Code': 'SWIS',
    'School District Code': 'School Code'
}, inplace=True)

# Remove unneeded cols
drop = ['Tax Class','Roll Section','Front','Depth','Deed Book','Page','Primary Owner First Name', 'Primary Owner MI', 'Primary Owner Last Name', 'Primary Owner Suffix',
        'Additional Owner 1 First Name', 'Additional Owner 1 MI', 'Additional Owner 1 Last Name', 'Additional Owner 1 Suffix', 'Additional Owner 2 First Name', 
        'Additional Owner 2 MI', 'Additional Owner 2 Last Name', 'Additional Owner 3 Last Name', 'Mailing Address Prefix', 'Mailing Address Number', 'Mailing Address Street', 
        'Mailing Address Suff', 'Mailing Address City','Parcel Address Number', 'Parcel Address Street', 'Parcel Address Suff', 'Bank', 
        'Mailing Address State', 'Mailing Address Zip', 'Mailing Address PO Box']
parcel = parcel.drop(drop, axis = 1)
print(parcel.columns.tolist())

# Subset of only 2021 data
tax = tax[tax['Roll Year'] == 2021]
parcel = parcel[parcel['Roll Year'] == 2021]

# Fix St lawrence naming
tax['County'] = tax['County'].replace('St. Lawrence', 'St Lawrence')
#%%#%% Subseting


### Property Class
classdisct = {931:'532a', 980:'Easments', 940:'Reforested/other',932:'532b',990:'Other'}

###############
pclass = 931
###############


taxcode = classdisct[pclass]
parcel = parcel[parcel['Property Class'] == pclass] #532a class


# class 931 = tax 532a Taxable Forest Preserve
# class 980 = Taxable state-owned conservation easements
# class 940 = Reforested land and other related conservation purposes
# class 932 = tax 532b Other State-owned land under Section 532-b, c, d, e, f, or g
# class 990 = Other taxable state land assessments

#%%

print(tax.columns.tolist())
merged_parcel_tax = pd.merge(parcel, tax, 
                            how='left', 
                            left_on=['County', 'School Code', 'Local SWIS'], 
                            right_on=['County', 'School Code', 'SWIS'], 
                            indicator=True)

# Find unmatched rows
unmatched_rows = merged_parcel_tax[merged_parcel_tax['_merge'] == 'left_only']

# Report unmatched data
if not unmatched_rows.empty:
    print("Unmatched data:")
    print(unmatched_rows)
    
# Export unmatched rows to CSV
    unmatched_rows.to_csv('Output/unmatched_data.csv', index=False)

#%%
merged_parcel_tax['Village Rate'] = merged_parcel_tax['Village Tax Rate (per $1000 value)'] / 1000
merged_parcel_tax['Village Tax Paid'] = merged_parcel_tax['Village Rate'] * merged_parcel_tax['Assessment Total'] /1000
total_assessment = merged_parcel_tax['Village Tax Paid'].sum()


