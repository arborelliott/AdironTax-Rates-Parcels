# -*- coding: utf-8 -*-
"""

@author: Jordan
"""

import pandas as pd
import matplotlib.pyplot as plt

#%% Import CSV files

tax_raw = pd.read_csv('Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv') 
tax = tax_raw

parcel_raw = pd.read_csv('Property_Assessment_Data_from_Local_Assessment_Rolls_931_980.csv')
parcel = parcel_raw

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
    'WIS Code': 'School Code',
    'Swis Code': 'Municipality Code'
}, inplace=True)

parcel.rename(columns={
    'County Name': 'County',
    'Swis Code': 'Municipality Code',
    'School District Code': 'School Code'
}, inplace=True)

#Subset of only 2021 data
tax = tax[tax['Roll Year'] == 2021]


#%% Subsetting ADK and Catskills

#Adks
adk_counties = ['Clinton', 'Essex', 'Franklin', 'Fulton', 'Hamilton', 'Herkimer', 'Lewis', 'Oneida', 'Saint Lawrence', 'Saratoga', 'Warren', 'Washington']
adk_munic = ['Altona', 'Arietta', 'Ausable', 'Bellmont', 'Benson', 'Black Brook', 'Bleecker', 'Bolton', 'Brighton',
             'Broadalbin', 'Caroga', 'Chester', 'Chesterfield', 'Clare', 'Clifton', 'Colton', 'Corinth', 'Croghan',
             'Crown Point', 'Dannemora', 'Day', 'Diana', 'Dresden', 'Duane', 'Edinburg', 'Elizabethtown',
             'Ellenburg', 'Ephratah', 'Essex', 'Fine', 'Forestport', 'Fort Ann', 'Franklin', 'Greenfield', 'Greig',
             'Hadley', 'Hague', 'Harrietstown', 'Hope', 'Hopkinton', 'Horicon', 'Indian Lake', 'Inlet', 'Jay',
             'Johnsburg', 'Johnstown', 'Keene', 'Lake George', 'Lake Luzerne', 'Lake Pleasant', 'Lawrence', 'Lewis',
             'Long Lake', 'Lyonsdale', 'Mayfield', 'Minerva', 'Morehouse', 'Moriah', 'Newcomb', 'North Elba',
             'North Hudson', 'Northampton', 'Ohio', 'Oppenheim', 'Parishville', 'Peru', 'Piercefield', 'Pitcairn',
             'Plattsburgh', 'Providence', 'Putnam', 'Queensbury', 'Remsen', 'Russia', 'Saint Armand', 'Salisbury',
             'Santa Clara', 'Saranac', 'Schroon', 'Stony Creek', 'Stratford', 'Thurman', 'Ticonderoga', 'Tupper Lake',
             'Warrensburg', 'Watson', 'Waverly', 'Webb', 'Wells', 'Westport', 'Willsboro', 'Wilmington', 'Corinth',
             'Dannemora', 'Lake George', 'Lake Placid', 'Mayfield', 'Northville', 'Saranac Lake', 'Speculator',
             'Tupper Lake']


adk_tax = tax[tax['County'].isin(adk_counties)]
adk_parcel = parcel[parcel['County'].isin(adk_counties)] #### Maybe this should be done after the merge??

### Add Catskills

#%% Calculating tax rates for each parcel

#County
adk_parcel_tax = pd.merge(adk_parcel, adk_tax[['County','County Tax Rate Outside Village (per $1000 value)','Municipal Tax Rate Outside Village (per $1000 value)','School District Tax Rate (per $1000 value)','School Code','Municipality Code']], how = 'left', left_on=['County','School Code','Municipality Code'], right_on=['County','School Code','Municipality Code'])
adk_parcel_tax['County Rate'] = adk_parcel_tax['County Tax Rate Outside Village (per $1000 value)'] / 1000

#Municipal
adk_parcel_tax['Municipal Rate'] = adk_parcel_tax['Municipal Tax Rate Outside Village (per $1000 value)'] / 1000

#School
adk_parcel_tax['School District Tax Rate (per $1000 value)'] = pd.to_numeric(adk_parcel_tax['School District Tax Rate (per $1000 value)'])
adk_parcel_tax['School Rate'] = adk_parcel_tax['School District Tax Rate (per $1000 value)'] / 1000


#%% Calculating parcel tax cost

#County
adk_parcel_tax['County Tax Paid'] = adk_parcel_tax['County Rate'] * adk_parcel_tax['County Taxable Value']

#Municipal
adk_parcel_tax['Municipal Tax Paid'] = adk_parcel_tax['Municipal Rate'] * adk_parcel_tax['Town Taxable Value']

#School
adk_parcel_tax['School Tax Paid'] = adk_parcel_tax['School Rate'] * adk_parcel_tax['School Taxable']

#Combined
adk_parcel_tax['Combined Tax Paid'] = adk_parcel_tax['School Tax Paid'] + adk_parcel_tax['County Tax Paid'] + adk_parcel_tax['Municipal Tax Paid']

adk_parcel_tax.to_csv('adk_parcel_tax.csv')