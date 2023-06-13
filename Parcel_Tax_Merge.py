# -*- coding: utf-8 -*-
"""

@author: Jordan Elliott

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
import re
plt.rcParams['figure.dpi'] = 300


#%% Importing files (tax, Parcel, Census)

# TAX levy data
tax_raw = pd.read_csv('Input/NYS_Tax_rates_Levy_Roll21.csv',dtype = {'FIPS_CODE':str,'STATE FIPS':str,'County FIPS':str,'Subdiv FIPS':str,'Place FIPS':str}) 
tax = tax_raw

# PARCEL of selected codes
parcel_raw = pd.read_csv('Input/Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv',dtype = {'Print Key Code':str})

# All PROPERTIES AND CODES ***VERY SLOW***  Only needed with first run
#parcel_raw = pd.read_csv('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.csv')
#parcel_raw.to_pickle('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.pkl')
#parcel_raw = pd.read_pickle('Input/Property_Assessment_Data_from_Local_Assessment_Rolls.pkl')

parcel = parcel_raw

# CENSUS
# Source: Retrieved from Census API
county_census = pd.read_excel('Output/Census/County_Census.xlsx',dtype = {'county':str})
subdiv_census = pd.read_excel('Output/Census/subdiv_Census.xlsx',dtype = {'county':str,'county subdivision':str})

# LOCALITY BUDGETS
# Source: https://wwe1.osc.state.ny.us/localgov/findata/financial-data-for-local-governments.cfm
# Files manually edited to remove un-needed formatting rows
county_budget = pd.read_excel('Input/Locality Spending/levelone21_county.xlsx')
town_budget = pd.read_excel('Input/Locality Spending/levelone21_town.xlsx')
school_budget = pd.read_excel('Input/Locality Spending/levelone21_schooldistrict.xlsx')

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
# print(parcel.columns.tolist())

# Subset of only 2021 data
tax = tax[tax['Roll Year'] == 2021]
parcel = parcel[parcel['Roll Year'] == 2021]


# Fix naming issues
tax['County'] = tax['County'].replace('St. Lawrence', 'St Lawrence')
parcel['Municipality Name'] = parcel['Municipality Name'].replace('Saratoga Springs, Outside', 'Saratoga Springs')

# Dropping not filed towns
county_budget = county_budget[county_budget['Real Property Taxes and Assessments'] != 'Not Filed']
town_budgetNA = town_budget[town_budget['Real Property Taxes and Assessments'] == 'Not Filed']
town_budget = town_budget[town_budget['Real Property Taxes and Assessments'] != 'Not Filed']


# Formatting name column for join 
county_budget['County'] = county_budget['County'].replace('St. Lawrence', 'St Lawrence')

# Function to remove specified words from a string using regular expressions
def remove_words(text, words):
    pattern = r'\b(?:{})\b'.format('|'.join(words))
    return re.sub(pattern, '', text, flags=re.IGNORECASE).strip()

words_to_remove = ["central", "school", "district","Free","City","Union","Common","Academy","and","High"]
school_budget['School District Name'] = school_budget['Entity Name'].apply(lambda x: remove_words(x, words_to_remove))

## Fixing Specific school names
replacements = {
    'Boquet Valley    at Elizabethtown-Lewis-Westport': 'Boquet Valley',
    'Oppenheim-Ephratah-St. Johnsville':'Oppenheim-Ephratah-St.Johnsvil',
    'Saint Regis Falls': 'St. Regis Falls',
    'Van Hornesville-Owen D Young':'Van Hornesville-Owen D. Young'}

school_budget['School District Name'] = school_budget['School District Name'].replace(replacements, regex=True)

#%% Merging Data

# print(tax.columns.tolist())
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
# if not unmatched_rows.empty:
#     print("Unmatched data:")
#     print(unmatched_rows)
    
# Export unmatched rows to CSV
    # unmatched_rows.to_csv('Output/unmatched_data.csv', index=False)

# Cleanup
#del unmatched_rows



#%% Calculating tax rates for each parcel

# County

merged_parcel_tax['County Rate'] = merged_parcel_tax['County Tax Rate Outside Village (per $1000 value)'] / 1000

# Municipal
merged_parcel_tax['Municipal Rate'] = merged_parcel_tax['Municipal Tax Rate Outside Village (per $1000 value)'] / 1000

# School
merged_parcel_tax['School District Tax Rate (per $1000 value)'] = pd.to_numeric(merged_parcel_tax['School District Tax Rate (per $1000 value)'])
merged_parcel_tax['School Rate'] = merged_parcel_tax['School District Tax Rate (per $1000 value)'] / 1000


#%% Calculating parcel tax cost

# County
merged_parcel_tax['Parcel County Tax Paid'] = merged_parcel_tax['County Rate'] * merged_parcel_tax['County Taxable Value'] /1000

# Municipal
merged_parcel_tax['Parcel Municipal Tax Paid'] = merged_parcel_tax['Municipal Rate'] * merged_parcel_tax['Town Taxable Value'] /1000

# School
merged_parcel_tax['Parcel School Tax Paid'] = merged_parcel_tax['School Rate'] * merged_parcel_tax['School Taxable'] /1000

# Combined
merged_parcel_tax['Parcel Combined Tax Paid'] = merged_parcel_tax['Parcel School Tax Paid'] + merged_parcel_tax['Parcel County Tax Paid'] + merged_parcel_tax['Parcel Municipal Tax Paid']



#%% Subsetting ADK and Catskills

#Adks
adk_counties = ['Clinton', 'Essex', 'Franklin', 'Fulton', 'Hamilton', 'Herkimer', 'Lewis', 'Oneida', 'St Lawrence', 'Saratoga', 'Warren', 'Washington']
adk_munic = pd.read_csv('Input/NYS_ADK_TOWNS.csv')
        
adk_villages = ['Corinth', 'Dannemora', 'Lake George', 'Lake Placid', 'Mayfield', 'Northville', 
        'Saranac Lake', 'Speculator', 'Tupper Lake',]
      
#antiquated subset based on county
#adk_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(adk_counties)]
adk_parcel_tax = merged_parcel_tax[merged_parcel_tax['SWIS'].isin(adk_munic['SWIS'])]


#Catskills
cat_counties = ['Delaware', 'Greene', 'Sullivan', 'Ulster']
cat_parcel_tax = merged_parcel_tax[merged_parcel_tax['County'].isin(cat_counties)]

# All Parcels 
all_parcel_tax = merged_parcel_tax

#%% Summary tables and graphs function

def export_tax_data(func_parcel_tax, prefix='', pclass ='' ):
    
    # Property Class subset
    classdisct = {931:'532a', 980:'Easments', 940:'Reforested_other',932:'532b',990:'Other'}
    taxcode = 'Allclass'
    
    if pclass != 'Allclass': # if pclass is not None, subset based on class code. 
        taxcode = classdisct[pclass]
        func_parcel_tax = func_parcel_tax[func_parcel_tax['Property Class'] == pclass]
   
    # Create File Path
    folder_path = f'Output/{taxcode}'

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # County summary table
    county_sum = func_parcel_tax.groupby(['County'])['Parcel County Tax Paid'].agg(['sum', 'mean', 'count']).reset_index() # create new DF grouped by county, aggregate sum, mean, count
    county_sum['County FIPS'] = func_parcel_tax.groupby('County')['County FIPS'].first().reset_index(drop=True) # inclue county FIPS code
    county_sum['sum'] = county_sum['sum'].round(2)
    
    ## County table (total row)
    total_sum = county_sum['sum'].sum()
    total_mean = county_sum['mean'].mean()
    total_count = county_sum['count'].sum() #calculate the sum, mean, and count for the columns
    
    total_row = pd.Series({'Locality':'County','County':'Total','sum': total_sum, 'mean': total_mean, 'count': total_count}, name=' County Total') # create new total row
    county_sum_total = county_sum.iloc[:] # add new row using values of total_row
    county_sum_total.loc[' County Total'] = total_row
    
    overall_total = pd.DataFrame(columns=['Locality','sum', 'mean', 'count'])
    overall_total = overall_total.iloc[:]
    overall_total.loc[0] = total_row
    
    # Municipality table
    munic_sum = func_parcel_tax.groupby(['Municipality Name'])['Parcel Municipal Tax Paid'].agg(['sum', 'mean', 'count']).reset_index()
    munic_sum['County'] = func_parcel_tax.groupby('Municipality Name')['County'].first().reset_index(drop=True)
    munic_sum['Subdiv FIPS'] = func_parcel_tax.groupby('Municipality Name')['Subdiv FIPS'].first().reset_index(drop=True)
    munic_sum['SWIS'] = func_parcel_tax.groupby('Municipality Name')['SWIS'].first().reset_index(drop=True).astype(str)
    munic_sum['sum'] = munic_sum['sum'].round(2)
    
    # Municipality table (total row)
    total_sum = munic_sum['sum'].sum()
    total_mean = munic_sum['mean'].mean()
    total_count = munic_sum['count'].sum()
    
    total_row = pd.Series({'Locality': 'Municipality','Municipality Name':'Total', 'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Municipality Total')
    munic_sum_total = munic_sum.iloc[:]
    munic_sum_total.loc[len(munic_sum_total)] = total_row
    
    overall_total = overall_total.iloc[:]
    overall_total.loc[len(overall_total)] = total_row
    
    # School table
    school_sum = func_parcel_tax.groupby(['School District Name'])['Parcel School Tax Paid'].agg(['sum', 'mean', 'count']).reset_index()
    school_sum['School Code'] = func_parcel_tax.groupby('School District Name')['School Code'].first().reset_index(drop=True).astype(str)
    school_sum['sum'] = school_sum['sum'].round(2)
    
    # School table (total row)
    total_sum = school_sum['sum'].sum()
    total_mean = school_sum['mean'].mean()
    total_count = school_sum['count'].sum()
    
    total_row = pd.Series({'Locality': 'School','School District Name':'Total','sum': total_sum, 'mean': total_mean, 'count': total_count}, name='School Total')
    school_sum_total = school_sum.iloc[:]
    school_sum_total.loc[len(school_sum_total)] = total_row
    
    overall_total = overall_total.iloc[:]
    overall_total.loc[len(overall_total)] = total_row
    
    # Overall Table
    total_sum = overall_total['sum'].sum()
    total_mean = overall_total['mean'].mean()
    total_count = school_sum['count'].sum()
    total_row = pd.Series({'Locality': 'Overall', 'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Overall Total')
    overall_total = overall_total.iloc[:]
    overall_total.loc[len(overall_total)] = total_row

                                                                         
    # Joining locality budgets to parcels
    ## County Budget to County Summary table
    county_sum_total = county_sum_total.merge(county_budget[['County','Real Property Taxes and Assessments',
                                                             'Local Revenues','Total Revenues']],
                                              on = 'County', how = 'left')
    ### Converting to (k)
    county_sum_total['County Real Property Taxes and Assessments (k)'] = county_sum_total['Real Property Taxes and Assessments'] /1000
    county_sum_total['County Local Revenues (k)'] = county_sum_total['Local Revenues'] /1000
    county_sum_total['County Total Revenues (k)'] = county_sum_total['Total Revenues'] /1000
    county_sum_total = county_sum_total.drop(['Real Property Taxes and Assessments', 
                                              'Local Revenues','Total Revenues'], axis = 1)
    
    
    ## Municipal budget to Municipal summary table
    town_budget['Municipality Name'] = town_budget['Entity Name'].str.replace('^Town of ', '', regex=True)
    town_budget['County'] = town_budget['County'].replace('St. Lawrence', 'St Lawrence')
    munic_sum_total = munic_sum_total.merge(town_budget[['Municipality Name','Real Property Taxes and Assessments',
                                                             'Local Revenues','Total Revenues','County']],
                                              on = ['Municipality Name','County'], 
                                              how = 'left', 
                                              indicator = True)
    failed_rows = munic_sum_total[munic_sum_total['_merge'] != 'both']
    #failed_rows.to_csv(f'Output/{taxcode}/{taxcode}_{prefix}_failed_munic_rows.csv') # Error Detecting
    munic_sum_total = munic_sum_total.drop(['_merge'],axis=1)
    
    ### Converting to (k)
    munic_sum_total['Municipality Real Property Taxes and Assessments (k)'] = munic_sum_total['Real Property Taxes and Assessments'] /1000
    munic_sum_total['Municipality Local Revenues (k)'] = munic_sum_total['Local Revenues'] /1000
    munic_sum_total['Municipality Total Revenues (k)'] = munic_sum_total['Total Revenues'] /1000
    munic_sum_total = munic_sum_total.drop(['Real Property Taxes and Assessments',
                                                             'Local Revenues','Total Revenues'], axis = 1)
    
    
    ## School Budget to School Summary Table
    school_sum_total = school_sum_total.merge(school_budget[['School District Name','Real Property Taxes and Assessments',
                                                             'Local Revenues','Total Revenues']],
                                              on = 'School District Name', how = 'left', indicator = True)
    
    # Use the below code to track schools which failed to merge
    #failed_rows = school_sum_total[school_sum_total['_merge'] != 'both']
    #failed_rows.to_csv('failed_school_rows.csv')
    school_sum_total = school_sum_total.drop(['_merge'],axis=1)
    
    ## Converting to (K)
    school_sum_total['School Real Property Taxes and Assessments (k)'] = school_sum_total['Real Property Taxes and Assessments'] /1000
    school_sum_total['School Local Revenues (k)'] = school_sum_total['Local Revenues'] /1000
    school_sum_total['School Total Revenues (k)'] = school_sum_total['Total Revenues'] /1000
    school_sum_total = school_sum_total.drop(['Real Property Taxes and Assessments',
                                                             'Local Revenues','Total Revenues'], axis = 1)

    # Calculating percentage of revenue from select tax
    ## County
    county_sum_total['% County Property revenue from select tax'] = county_sum_total['sum'] / county_sum_total['County Real Property Taxes and Assessments (k)']
    county_sum_total['% County Local revenue from select tax'] = county_sum_total['sum'] / county_sum_total['County Local Revenues (k)']
    county_sum_total['% County Total revenue from select tax'] = county_sum_total['sum'] / county_sum_total['County Total Revenues (k)']

    ## Town
    munic_sum_total['% Municipality Property revenue from select tax'] = munic_sum_total['sum'] / munic_sum_total['Municipality Real Property Taxes and Assessments (k)']
    munic_sum_total['% Municipality Local revenue from select tax'] = munic_sum_total['sum'] / munic_sum_total['Municipality Local Revenues (k)']
    munic_sum_total['% Municipality Total revenue from select tax'] = munic_sum_total['sum'] / munic_sum_total['Municipality Total Revenues (k)']

    ## School
    school_sum_total['% School Property revenue from select tax'] = school_sum_total['sum'] / school_sum_total['School Real Property Taxes and Assessments (k)']
    school_sum_total['% School Local revenue from select tax'] = school_sum_total['sum'] / school_sum_total['School Local Revenues (k)']
    school_sum_total['% School Total revenue from select tax'] = school_sum_total['sum'] / school_sum_total['School Total Revenues (k)'] 

    # Locality totals joined to main parcels list
    # County
    func_parcel_tax = func_parcel_tax.merge(county_sum_total[['County', 'sum', 'County FIPS',
                                                               'County Real Property Taxes and Assessments (k)', 'County Local Revenues (k)', 
                                                               'County Total Revenues (k)', '% County Property revenue from select tax', 
                                                               '% County Local revenue from select tax', '% County Total revenue from select tax']],
                                            on='County FIPS', how='left')
    func_parcel_tax = func_parcel_tax.rename(columns={'sum': 'Total County Select Tax Received (k)'})
    
    # Munic
    func_parcel_tax = func_parcel_tax.merge(munic_sum_total[['Municipality Name', 'sum', 'Subdiv FIPS', 'Municipality Real Property Taxes and Assessments (k)', 
                                                             'Municipality Local Revenues (k)', 'Municipality Total Revenues (k)', '% Municipality Property revenue from select tax', 
                                                             '% Municipality Local revenue from select tax', '% Municipality Total revenue from select tax']],
                                            on='Subdiv FIPS', how='left')
    func_parcel_tax = func_parcel_tax.rename(columns={'sum': 'Total Municipal Select Tax Received (k)'})
    
    # School
    func_parcel_tax = func_parcel_tax.merge(school_sum_total[['School District Name', 'sum', 'School Real Property Taxes and Assessments (k)', 'School Local Revenues (k)',
                                                             'School Total Revenues (k)', '% School Property revenue from select tax', '% School Local revenue from select tax',
                                                             '% School Total revenue from select tax']],
                                           on='School District Name', how='left')
    func_parcel_tax = func_parcel_tax.rename(columns={'sum': 'Total School Select Tax Received (k)'})

    # Graphs
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
       
    # Percentages
    # County Local Revenue from {taxcode} Tax by County
    county_names = county_sum_total['County'].astype(str)
    plt.barh(county_names, county_sum_total['% County Local revenue from select tax'], color='orange')
    plt.xlabel(f'% of County Local Revenue from {taxcode} Tax')
    plt.ylabel('County')
    plt.title(f'Percentage of {prefix} County Local Revenue from {taxcode} Tax by County')
    plt.yticks(rotation=0)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_county_percent.png')
    plt.show()
    del county_names
    
    # Municipality Local Revenue from {taxcode} Tax by Municipality
    munic_names = munic_sum_total['Municipality Name'].astype(str)
    plt.barh(munic_names, munic_sum_total['% Municipality Local revenue from select tax'], color='orange')
    plt.xlabel(f'% of Municipality Local Revenue from {taxcode} Tax')
    plt.ylabel('Municipality')
    plt.title(f'Percentage of {prefix} Municipality Local Revenue from {taxcode} Tax by Municipality')
    plt.yticks(rotation=0, fontsize=5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_Municipality_percent.png')
    plt.show()
    del munic_names
    
    # School Local Revenue from {taxcode} Tax by School
    school_names = school_sum_total['School District Name'].astype(str)
    plt.barh(school_names, school_sum_total['% School Local revenue from select tax'], color='orange')
    plt.xlabel(f'% of School Local Revenue from {taxcode} Tax')
    plt.ylabel('School')
    plt.title(f'Percentage of {prefix} School Local Revenue from {taxcode} Tax by School')
    plt.yticks(rotation=0, fontsize=5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_school_sum_total.png')
    plt.show()
    del school_names


    # Totals
    # Sum of County Tax Paid on {taxcode} by County
    plt.barh(county_sum['County'], county_sum['sum'], color = 'blue')
    plt.xlabel('Sum of County Tax Paid (in k)')
    plt.ylabel('County')
    plt.title(f'{prefix} Sum of County Tax Paid on {taxcode} by County')
    plt.yticks(rotation=0)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_county_sum.png')
    plt.show()
    
    # Sum of Municipality Tax Paid on {taxcode} by Municipality
    plt.barh(munic_sum['Municipality Name'], munic_sum['sum'], color = 'blue')
    plt.xlabel('Sum of Municipality Tax Paid (in k)')
    plt.ylabel('Municipality')
    plt.title(f'{prefix} Sum of Municipality Tax Paid on {taxcode} by Municipality')
    plt.yticks(rotation=0, fontsize=5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_Municipality_sum.png')
    plt.show()
    
    # Sum of School Tax Paid on {taxcode} by School
    plt.barh(school_sum['School District Name'], school_sum['sum'], color = 'blue')
    plt.xlabel('Sum of School Tax Paid (in k)')
    plt.ylabel('School')
    plt.title(f'{prefix} Sum of School Tax Paid on {taxcode} by School')
    plt.yticks(rotation=0, fontsize=5)
    plt.savefig(f'Output/{taxcode}/{taxcode}_{prefix}_School_sum.png')
    plt.show()


    
    # Renaming sum column in all datasets
    county_sum_total = county_sum_total.rename(columns={'sum': 'Total County Select Tax Received (k)'})
    munic_sum_total = munic_sum_total.rename(columns={'sum': 'Total Municipal Select Tax Received (k)'})
    school_sum_total = school_sum_total.rename(columns={'sum': 'Total School Select Tax Received (k)'})
    
    # Merging With Census Data
    county_sum_total = county_sum_total.merge(county_census, left_on='County FIPS', right_on='county',how = 'left')
    county_sum_total = county_sum_total.drop(['NAME','COUNTY','Unnamed: 0',
                                              'GEO_ID','state','county'],axis = 1)
    
    munic_sum_total = munic_sum_total.merge(subdiv_census, left_on='Subdiv FIPS', right_on='county subdivision',how = 'left')
    munic_sum_total = munic_sum_total.drop(['NAME','COUNTY','Unnamed: 0',
                                              'GEO_ID','state','county'],axis = 1)
    
    # Making sure codes are strings
    munic_sum_total['SWIS'] = munic_sum_total['SWIS'].astype(str)
    school_sum_total['School Code'] = school_sum_total['School Code'].astype(str)
    
    # Cleanup
    del [total_sum, total_mean, total_count, total_row]
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
'''
    Data Export function (region set, prefix, pclass)
        Regions: cat_parcel_tax, adk_parcel_tax, all_parcel_tax
        
        Prefix: This is the naming convention which will attach to each file output
        
        Property Classes:
            class 931 = tax 532a Taxable Forest Preserve
            class 980 = Taxable state-owned conservation easements
            class 940 = Reforested land and other related conservation purposes
            class 932 = tax 532b Other State-owned land under Section 532-b, c, d, e, f, or g
            class 990 = Other taxable state land assessments
'''

export_tax_data(cat_parcel_tax, prefix='Cat', pclass =931)
export_tax_data(adk_parcel_tax, prefix='Adk', pclass =931)
# export_tax_data(all_parcel_tax, prefix='all', pclass =931)

## adk/cat region, all parcels, all tax codes. 
#export_tax_data(all_parcel_tax, prefix='all', pclass ='Allclass')


