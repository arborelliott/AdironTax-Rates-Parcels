# -*- coding: utf-8 -*-
"""

@author: Jordan

NOTES: 
    report failed merge items
    Summary of all totals
"""

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300

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

#subset of only 532a parcels
parcel = parcel[parcel['Property Class'] == 931] #532a class
parcel = parcel[parcel['Roll Year'] == 2021]

#%% Merging Data
merged_parcel_tax = pd.merge(parcel, tax[['County','County Tax Rate Outside Village (per $1000 value)','Municipal Tax Rate Outside Village (per $1000 value)','School District Tax Rate (per $1000 value)','School Code','Municipality Code']], how = 'left', left_on=['County','School Code','Municipality Code'], right_on=['County','School Code','Municipality Code'])

#%% Merging and Calculating tax rates for each parcel

#County

merged_parcel_tax['County Rate'] = merged_parcel_tax['County Tax Rate Outside Village (per $1000 value)'] / 1000

#Municipal
merged_parcel_tax['Municipal Rate'] = merged_parcel_tax['Municipal Tax Rate Outside Village (per $1000 value)'] / 1000

#School
merged_parcel_tax['School District Tax Rate (per $1000 value)'] = pd.to_numeric(merged_parcel_tax['School District Tax Rate (per $1000 value)'])
merged_parcel_tax['School Rate'] = merged_parcel_tax['School District Tax Rate (per $1000 value)'] / 1000


#%% Calculating parcel tax cost

#County
merged_parcel_tax['County Tax Paid'] = merged_parcel_tax['County Rate'] * merged_parcel_tax['County Taxable Value'] /1000

#Municipal
merged_parcel_tax['Municipal Tax Paid'] = merged_parcel_tax['Municipal Rate'] * merged_parcel_tax['Town Taxable Value'] /1000

#School
merged_parcel_tax['School Tax Paid'] = merged_parcel_tax['School Rate'] * merged_parcel_tax['School Taxable'] /1000

#Combined
merged_parcel_tax['Combined Tax Paid'] = merged_parcel_tax['School Tax Paid'] + merged_parcel_tax['County Tax Paid'] + merged_parcel_tax['Municipal Tax Paid']



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


adk_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(adk_counties)]


#Catskills

cat_counties = ['Delaware', 'Greene', 'Sullivan', 'Ulster']
cat_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(cat_counties)]


#%% Summarizing ADK

#County table
adk_county_sum = adk_parcel_tax.groupby(['County'])['County Tax Paid'].agg(['sum','mean','count'])
adk_county_sum['sum'] = adk_county_sum['sum'].round(2)

#   County table total
total_sum = adk_county_sum['sum'].sum()
total_mean = adk_county_sum['mean'].mean()
total_count = adk_county_sum['count'].sum()

total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name=' County Total')
adk_county_sumtotal = adk_county_sum.append(total_row)
    
#   Overall table total
adk_overall_total = pd.DataFrame(columns=['sum', 'mean', 'count'])
adk_overall_total = adk_overall_total.append(total_row)

# Municipality table
adk_munic_sum = adk_parcel_tax.groupby(['Municipality Name'])['Municipal Tax Paid'].agg(['sum','mean','count'])
adk_munic_sum['sum'] = adk_munic_sum['sum'].round(2)

#   Municipality table total
total_sum = adk_munic_sum['sum'].sum()
total_mean = adk_munic_sum['mean'].mean()
total_count = adk_munic_sum['count'].sum()

total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Municipality Total')
adk_munic_sumtotal = adk_munic_sum.append(total_row)

#   Overall table total
adk_overall_total = adk_overall_total.append(total_row)

# School table
adk_school_sum = adk_parcel_tax.groupby(['School District Name'])['School Tax Paid'].agg(['sum','mean','count'])
adk_school_sum['sum'] = adk_school_sum['sum'].round(2)

#   School table total
total_sum = adk_school_sum['sum'].sum()
total_mean = adk_school_sum['mean'].mean()
total_count = adk_school_sum['count'].sum()

total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='School Total')

adk_school_sumtotal = adk_school_sum.append(total_row)

# Overall Table

total_sum = adk_overall_total['sum'].sum()
total_mean = adk_overall_total['mean'].mean()
total_count = adk_school_sum['count'].sum()
total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Overall Total')
adk_overall_total = adk_overall_total.append(total_row)

#All 3
# adk_all3_sum = adk_parcel_tax.groupby(['County','Municipality Name','School District Name'])['School Tax Paid'].agg(['sum','mean','count'])
# adk_all3_sum['sum'] = adk_all3_sum['sum'].round(2)
#### need to add for other 2 taxes paid and export these to csv? Also convert to in millions?

#Exporting to excel

with pd.ExcelWriter('Output/adk_parcel_tax.xlsx',date_format=None, mode='w') as writer:
    adk_parcel_tax.to_excel(writer, sheet_name = 'All Parcels')
    adk_county_sumtotal.to_excel(writer, sheet_name = 'County Summary')
    adk_munic_sumtotal.to_excel(writer, sheet_name = 'Municipality Summary')
    adk_school_sumtotal.to_excel(writer, sheet_name = 'School Summary')
    adk_overall_total.to_excel(writer, sheet_name = 'Overall Summary')

#%% Summarizing Catskills

#County
cat_county_sum = cat_parcel_tax.groupby(['County'])['County Tax Paid'].agg(['sum','mean','count'])
cat_county_sum['sum'] = cat_county_sum['sum'].round(2)

#Municipality
cat_munic_sum = cat_parcel_tax.groupby(['Municipality Name'])['Municipal Tax Paid'].agg(['sum','mean','count'])
cat_munic_sum['sum'] = cat_munic_sum['sum'].round(2)

#School
cat_school_sum = cat_parcel_tax.groupby(['School District Name'])['School Tax Paid'].agg(['sum','mean','count'])
cat_school_sum['sum'] = cat_school_sum['sum'].round(2)

#All 3
# adk_all3_sum = adk_parcel_tax.groupby(['County','Municipality Name','School District Name'])['School Tax Paid'].agg(['sum','mean','count'])
# adk_all3_sum['sum'] = adk_all3_sum['sum'].round(2)
#### need to add for other 2 taxes paid and export these to csv? Also convert to in millions?

#Exporting to excel

with pd.ExcelWriter('Output/cat_parcel_tax.xlsx',date_format=None, mode='w') as writer:
    cat_parcel_tax.to_excel(writer, sheet_name = 'All Parcels')
    cat_county_sum.to_excel(writer, sheet_name = 'County Summary')
    cat_munic_sum.to_excel(writer, sheet_name = 'Municipality Summary')
    cat_school_sum.to_excel(writer, sheet_name = 'School Summary')



#%% ADK Graphics
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["figure.figsize"] = [7.00, 7.00]
plt.rcParams["figure.autolayout"] = True

plt.barh(adk_county_sum.index, adk_county_sum['sum'])
plt.xlabel('Sum of County Tax Paid')
plt.ylabel('County')
plt.title('Sum of County Tax Paid by County (Thousands)')
plt.yticks(rotation=0)
plt.savefig('Output/adk_county_sum.png')
plt.show()

plt.barh(adk_munic_sum.index, adk_munic_sum['sum'])
plt.ylabel('Municipality')
plt.xlabel('Sum of Municipality Tax Paid')
plt.title('Sum of Municipality Tax Paid by Municipality (Thousands)')
plt.yticks(rotation=0, fontsize = 5)
plt.savefig('Output/adk_Municipality_sum.png')
plt.show()

plt.barh(adk_school_sum.index, adk_school_sum['sum'])
plt.ylabel('School')
plt.xlabel('Sum of School Tax Paid')
plt.title('Sum of School Tax Paid by School (Thousands)')
plt.yticks(rotation=0, fontsize = 5)
plt.savefig('Output/adk_School_sum.png')
plt.show()


