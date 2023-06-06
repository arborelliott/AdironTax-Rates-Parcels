# -*- coding: utf-8 -*-
"""

@author: Jordan

3. This should be run after Boundaries_Merge and census_api
    This script imports tax rate data from the previous script, and parcel data from assessment rolls. 
    The Script cleans the data, subsets to a given year and property class, and merges the parcel data with the tax rate data to calculate the amount of taxes paid on each parcel. 
    The script outputs 3 graphs per region of interest, and an excel file summarizing the findings.  
    
    INPUT:
        1. NYS_Tax_rates_Levy_Roll21.csv (From Boundaries_Merge.py)
        2. Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv - Assessment rolls from NYS
        3. Census data (From Census_api), ex: Census/County_Census.xlsx
    OUTPUT:
        {taxcode}_{prefix}_parcel_tax.xlsx - Summary of state tax expenditure by locality. 
        
    VARIABLES:
        Property class
        Tax year
        

NOTES: 
    Switch subsetting to municipalities instead of counties

    
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
plt.rcParams['figure.dpi'] = 300


#%% Importing files (tax, Parcel, Census)

# TAX
#tax_raw = pd.read_csv('Input/Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv') 
tax_raw = pd.read_csv('Input/NYS_Tax_rates_Levy_Roll21.csv',dtype = {'FIPS_CODE':str,'STATE FIPS':str,'County FIPS':str,'Subdiv FIPS':str,'Place FIPS':str}) 
tax = tax_raw

# PARCEL
#   Select Codes
parcel_raw = pd.read_csv('Input/Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv',dtype = {'Print Key Code':str})

#   All PROPERTIES AND CODES ***VERY SLOW***
#       Only needed with first run
#parcel_raw = pd.read_csv('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.csv')
#parcel_raw.to_pickle('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.pkl')

#parcel_raw = pd.read_pickle('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.pkl')

#
parcel = parcel_raw

# CENSUS
county_census = pd.read_excel('Output/Census/County_Census.xlsx',dtype = {'county':str})
subdiv_census = pd.read_excel('Output/Census/subdiv_Census.xlsx',dtype = {'county':str,'county subdivision':str})


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



#%% Merging Data

print(tax.columns.tolist())
merged_parcel_tax = pd.merge(parcel, tax[['County', 'County Tax Rate Outside Village (per $1000 value)', 'Municipal Tax Rate Outside Village (per $1000 value)',
                                          'School District Tax Rate (per $1000 value)', 'School Code', 'SWIS','MUNI_TYPE','FIPS_CODE', 'State FIPS', 'County FIPS', 'Subdiv FIPS', 
                                          'POP1990', 'POP2000', 'POP2010', 'POP2020', 'CALC_SQ_MI']], 
                            how='left', 
                            left_on=['County', 'School Code', 'SWIS'], 
                            right_on=['County', 'School Code', 'SWIS'], 
                            indicator=True)

# Saving FIPS column as string


# Find unmatched rows
unmatched_rows = merged_parcel_tax[merged_parcel_tax['_merge'] == 'left_only']

# Report unmatched data
if not unmatched_rows.empty:
    print("Unmatched data:")
    print(unmatched_rows)
    
# Export unmatched rows to CSV
    unmatched_rows.to_csv('Output/unmatched_data.csv', index=False)

# Cleanup
#del unmatched_rows



#%% Merging and Calculating tax rates for each parcel

# County

merged_parcel_tax['County Rate'] = merged_parcel_tax['County Tax Rate Outside Village (per $1000 value)'] / 1000

# Municipal
merged_parcel_tax['Municipal Rate'] = merged_parcel_tax['Municipal Tax Rate Outside Village (per $1000 value)'] / 1000

# School
merged_parcel_tax['School District Tax Rate (per $1000 value)'] = pd.to_numeric(merged_parcel_tax['School District Tax Rate (per $1000 value)'])
merged_parcel_tax['School Rate'] = merged_parcel_tax['School District Tax Rate (per $1000 value)'] / 1000


#%% Calculating parcel tax cost

# County
merged_parcel_tax['County Tax Paid'] = merged_parcel_tax['County Rate'] * merged_parcel_tax['County Taxable Value'] /1000

# Municipal
merged_parcel_tax['Municipal Tax Paid'] = merged_parcel_tax['Municipal Rate'] * merged_parcel_tax['Town Taxable Value'] /1000

# School
merged_parcel_tax['School Tax Paid'] = merged_parcel_tax['School Rate'] * merged_parcel_tax['School Taxable'] /1000

# Combined
merged_parcel_tax['Combined Tax Paid'] = merged_parcel_tax['School Tax Paid'] + merged_parcel_tax['County Tax Paid'] + merged_parcel_tax['Municipal Tax Paid']



#%% Subsetting ADK and Catskills

#Adks
adk_counties = ['Clinton', 'Essex', 'Franklin', 'Fulton', 'Hamilton', 'Herkimer', 'Lewis', 'Oneida', 'St Lawrence', 'Saratoga', 'Warren', 'Washington']
adk_munic = ['Altona', 'Arietta', 'AuSable', 'Bellmont', 'Benson', 'Black Brook', 
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
        # End village list 
        'Warrensburg', 'Watson', 'Waverly', 'Webb', 'Wells', 'Westport', 
        'Willsboro', 'Wilmington']
        
adk_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(adk_counties)]

#Catskills
cat_counties = ['Delaware', 'Greene', 'Sullivan', 'Ulster']
cat_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(cat_counties)]

# All Parcels 
all_parcel_tax = merged_parcel_tax

#%% Summary tables and graphs function

def export_tax_data(func_parcel_tax, prefix='', pclass ='' ):
    
    
    
    ### Property Class
    classdisct = {931:'532a', 980:'Easments', 940:'Reforested_other',932:'532b',990:'Other'}

    ###############
    ###############

    taxcode = 'Allclass'
    
    if pclass != 'Allclass': # if pclass is not None, subset based on class code. 
        taxcode = classdisct[pclass]
        func_parcel_tax = func_parcel_tax[func_parcel_tax['Property Class'] == pclass]



    # class 931 = tax 532a Taxable Forest Preserve
    # class 980 = Taxable state-owned conservation easements
    # class 940 = Reforested land and other related conservation purposes
    # class 932 = tax 532b Other State-owned land under Section 532-b, c, d, e, f, or g
    # class 990 = Other taxable state land assessments
   
    # Create File Path
    folder_path = f'Output/{taxcode}'

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # County table
    county_sum = func_parcel_tax.groupby(['County'])['County Tax Paid'].agg(['sum', 'mean', 'count']).reset_index()
    county_sum['County FIPS'] = func_parcel_tax.groupby('County')['County FIPS'].first().reset_index(drop=True) # inclue county FIPS code
    county_sum['sum'] = county_sum['sum'].round(2)
    
    # County table (total row)
    total_sum = county_sum['sum'].sum()
    total_mean = county_sum['mean'].mean()
    total_count = county_sum['count'].sum()
    
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name=' County Total')
    county_sum_total = county_sum.append(total_row)
    
    overall_total = pd.DataFrame(columns=['sum', 'mean', 'count'])
    overall_total = overall_total.append(total_row)
    
    # Municipality table 
    munic_sum = func_parcel_tax.groupby(['Municipality Name'])['Municipal Tax Paid'].agg(['sum', 'mean', 'count']).reset_index()
    munic_sum['Subdiv FIPS'] = func_parcel_tax.groupby('Municipality Name')['Subdiv FIPS'].first().reset_index(drop=True)
    munic_sum['sum'] = munic_sum['sum'].round(2)
    
    # Municipality table (total row)
    total_sum = munic_sum['sum'].sum()
    total_mean = munic_sum['mean'].mean()
    total_count = munic_sum['count'].sum()
    
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Municipality Total')
    munic_sum_total = munic_sum.append(total_row)
    
    overall_total = overall_total.append(total_row)
    
    # School table
    school_sum = func_parcel_tax.groupby(['School District Name'])['School Tax Paid'].agg(['sum', 'mean', 'count']).reset_index()
    school_sum['sum'] = school_sum['sum'].round(2)
    
    # School table (total row)
    total_sum = school_sum['sum'].sum()
    total_mean = school_sum['mean'].mean()
    total_count = school_sum['count'].sum()
    
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='School Total')
    school_sum_total = school_sum.append(total_row)
    overall_total = overall_total.append(total_row)
    
    # Overall Table 
    total_sum = overall_total['sum'].sum()
    total_mean = overall_total['mean'].mean()
    total_count = school_sum['count'].sum()
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Overall Total')
    overall_total = overall_total.append(total_row)
    
    
    ## Graphs
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    
    plt.barh(county_sum['County'], county_sum['sum'])
    plt.xlabel('Sum of County Tax Paid')
    plt.ylabel('County')
    plt.title(f'{prefix} Sum of County Tax Paid on {taxcode} by County (Thousands)')
    plt.yticks(rotation=0)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_county_sum.png')
    plt.show()
    
    plt.barh(munic_sum['Municipality Name'], munic_sum['sum'])
    plt.ylabel('Municipality')
    plt.xlabel('Sum of Municipality Tax Paid')
    plt.title(f'{prefix} Sum of Municipality Tax Paid on {taxcode} by Municipality (Thousands)')
    plt.yticks(rotation=0, fontsize = 5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_Municipality_sum.png')
    plt.show()
    
    plt.barh(school_sum['School District Name'], school_sum['sum'])
    plt.ylabel('School')
    plt.xlabel('Sum of School Tax Paid')
    plt.title(f'{prefix} Sum of School Tax Paid on {taxcode} by School (Thousands)')
    plt.yticks(rotation=0, fontsize = 5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_School_sum.png')
    plt.show()
    
    ## Cleanup
    del [total_sum, total_mean, total_count, total_row]
    
    # Renaming sum column in all datasets
    datasets = [county_sum_total, munic_sum_total, school_sum_total, overall_total]
    for dataset in datasets:
        dataset.rename(columns={'sum': 'sum (thousands)'}, inplace=True)
    del [dataset, datasets]
    
    # Merging With Census Data
    county_sum_total = county_sum_total.merge(county_census, left_on='County FIPS', right_on='county').reset_index()
    county_sum_total = county_sum_total.drop(['NAME','COUNTY','Unnamed: 0',
                                              'GEO_ID','state','county'],axis = 1)
    
    munic_sum_total = munic_sum_total.merge(subdiv_census, left_on='Subdiv FIPS', right_on='county subdivision').reset_index()
    munic_sum_total = munic_sum_total.drop(['NAME','COUNTY','Unnamed: 0',
                                              'GEO_ID','state','county'],axis = 1)
    
    # Cleanup
    func_parcel_tax = func_parcel_tax.drop('_merge',axis = 1)
    func_parcel_tax['Print Key Code'] = func_parcel_tax['Print Key Code'].astype(str)
    
    
    # Export to Excel
    with pd.ExcelWriter(f'Output/{taxcode}/{taxcode}_{prefix}_parcel_tax.xlsx',date_format=None, mode='w',) as writer:
        func_parcel_tax.to_excel(writer, sheet_name = f'{taxcode} All Parcels')
        county_sum_total.to_excel(writer, sheet_name = 'County Summary')
        munic_sum_total.to_excel(writer, sheet_name = 'Municipality Summary')
        school_sum_total.to_excel(writer, sheet_name = 'School Summary')
        overall_total.to_excel(writer, sheet_name = 'Overall Summary')
                
#%% Functions
###### Data Export functions

#export_tax_data(cat_parcel_tax, prefix='cat', pclass =931)
#export_tax_data(adk_parcel_tax, prefix='adk', pclass =931)
#export_tax_data(all_parcel_tax, prefix='all', pclass =931)

# adk/cat region, all parcels, all tax codes. 
export_tax_data(all_parcel_tax, prefix='all', pclass ='Allclass')
######
