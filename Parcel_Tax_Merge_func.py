# -*- coding: utf-8 -*-
"""

@author: Jordan

NOTES: 
    
"""

import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300

#%% Import CSV files

tax_raw = pd.read_csv('Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv') 
tax = tax_raw

parcel_raw = pd.read_csv('Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv')
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

# Subset of only 2021 data
tax = tax[tax['Roll Year'] == 2021]
parcel = parcel[parcel['Roll Year'] == 2021]

# Fix St lawrence naming
tax['County'] = tax['County'].replace('St. Lawrence', 'St Lawrence')


#%% Subset of only 532a parcels


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




#%% Merging Data
#merged_parcel_tax = pd.merge(parcel, tax[['County','County Tax Rate Outside Village (per $1000 value)','Municipal Tax Rate Outside Village (per $1000 value)','School District Tax Rate (per $1000 value)','School Code','Municipality Code']], how = 'left', left_on=['County','School Code','Municipality Code'], right_on=['County','School Code','Municipality Code'])


merged_parcel_tax = pd.merge(parcel, tax[['County', 'County Tax Rate Outside Village (per $1000 value)', 'Municipal Tax Rate Outside Village (per $1000 value)', 'School District Tax Rate (per $1000 value)', 'School Code', 'Municipality Code']], 
                            how='left', 
                            left_on=['County', 'School Code', 'Municipality Code'], 
                            right_on=['County', 'School Code', 'Municipality Code'], 
                            indicator=True)

# Find unmatched rows
unmatched_rows = merged_parcel_tax[merged_parcel_tax['_merge'] == 'left_only']

# Report unmatched data
if not unmatched_rows.empty:
    print("Unmatched data:")
    print(unmatched_rows)
    
# Export unmatched rows to CSV
    #unmatched_rows.to_csv('Output/unmatched_data.csv', index=False)

# Cleanup
del unmatched_rows


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


#%% Summary tables and graphs function

def export_tax_data(func_parcel_tax, prefix=''):
    
    # County table
    county_sum = func_parcel_tax.groupby(['County'])['County Tax Paid'].agg(['sum', 'mean', 'count'])
    county_sum['sum'] = county_sum['sum'].round(2)
    
    # County table total
    total_sum = county_sum['sum'].sum()
    total_mean = county_sum['mean'].mean()
    total_count = county_sum['count'].sum()
    
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name=' County Total')
    county_sum_total = county_sum.append(total_row)
    
    # Overall table total
    overall_total = pd.DataFrame(columns=['sum', 'mean', 'count'])
    overall_total = overall_total.append(total_row)
    
    # Municipality table
    munic_sum = func_parcel_tax.groupby(['Municipality Name'])['Municipal Tax Paid'].agg(['sum', 'mean', 'count'])
    munic_sum['sum'] = munic_sum['sum'].round(2)
    
    # Municipality table total
    total_sum = munic_sum['sum'].sum()
    total_mean = munic_sum['mean'].mean()
    total_count = munic_sum['count'].sum()
    
    total_row = pd.Series({'sum': total_sum, 'mean': total_mean, 'count': total_count}, name='Municipality Total')
    munic_sum_total = munic_sum.append(total_row)
    
    # Overall table total
    overall_total = overall_total.append(total_row)
    
    # School table
    school_sum = func_parcel_tax.groupby(['School District Name'])['School Tax Paid'].agg(['sum', 'mean', 'count'])
    school_sum['sum'] = school_sum['sum'].round(2)
    
    # School table total
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
    
    # Graphs
    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["figure.figsize"] = [7.00, 7.00]
    plt.rcParams["figure.autolayout"] = True
    
    plt.barh(county_sum.index, county_sum['sum'])
    plt.xlabel('Sum of County Tax Paid')
    plt.ylabel('County')
    plt.title(f'{prefix} Sum of County Tax Paid on {taxcode} by County (Thousands)')
    plt.yticks(rotation=0)
    plt.savefig(f'Output/{taxcode}_{prefix}_county_sum.png')
    plt.show()
    
    plt.barh(munic_sum.index, munic_sum['sum'])
    plt.ylabel('Municipality')
    plt.xlabel('Sum of Municipality Tax Paid')
    plt.title(f'{prefix} Sum of Municipality Tax Paid on {taxcode} by Municipality (Thousands)')
    plt.yticks(rotation=0, fontsize = 5)
    plt.savefig(f'Output/{taxcode}_{prefix}_Municipality_sum.png')
    plt.show()
    
    plt.barh(school_sum.index, school_sum['sum'])
    plt.ylabel('School')
    plt.xlabel('Sum of School Tax Paid')
    plt.title(f'{prefix} Sum of School Tax Paid on {taxcode} by School (Thousands)')
    plt.yticks(rotation=0, fontsize = 5)
    plt.savefig(f'Output/{taxcode}_{prefix}_School_sum.png')
    plt.show()
    
    # Cleanup
    del [total_sum, total_mean, total_count, total_row]
    
    # Renaming sum column in all datasets
    datasets = [county_sum_total, munic_sum_total, school_sum_total, overall_total]
    for dataset in datasets:
        dataset.rename(columns={'sum': 'sum (thousands)'}, inplace=True)
    del [dataset, datasets]
    
    # Export to Excel
    with pd.ExcelWriter(f'Output/{taxcode}_{prefix}_parcel_tax.xlsx',date_format=None, mode='w') as writer:
        func_parcel_tax.to_excel(writer, sheet_name = f'{taxcode} All Parcels')
        county_sum_total.to_excel(writer, sheet_name = 'County Summary')
        munic_sum_total.to_excel(writer, sheet_name = 'Municipality Summary')
        school_sum_total.to_excel(writer, sheet_name = 'School Summary')
        overall_total.to_excel(writer, sheet_name = 'Overall Summary')

#%% Functions
###### Data Export functions
export_tax_data(cat_parcel_tax, prefix='cat')
export_tax_data(adk_parcel_tax, prefix='adk')
######

