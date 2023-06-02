# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:10:35 2023

@author: chris
"""

import pandas as pd

#%% Importing csv files. Dwnloaded all real estate transacitons from a 
#   ten year period from counties that contain the Adirondack Park. 

clinton_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/0914_19.CSV', index_col=False)
clinton_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/0920_CUR.CSV', index_col=False)

essex_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/1514_19.CSV', index_col=False)
essex_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/1520_CUR.CSV', index_col=False)

franklin_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/1614_19.CSV', index_col=False)
frankin_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/1620_CUR.CSV', index_col=False)

fulton_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/1714_19.CSV', index_col=False)
fulton_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/1720_CUR.CSV', index_col=False)

hamilton_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/2014_19.CSV', index_col=False)
hamilton_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/2020_CUR.CSV', index_col=False)

herkimer_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/2114_19.CSV', index_col=False)
hermiker_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/2120_CUR.CSV', index_col=False)

#Manually deleted row 8674 due to typo in print key. 
lewis_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/2314_19.CSV', index_col=False)
lewis_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/2320_CUR.CSV', index_col=False)

oneida_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/3014_19.CSV', index_col=False)
oneida_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/3020_CUR.CSV', index_col=False)

st_lawrence_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/4014_19.CSV', index_col=False)
st_lawrence_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/4020_CUR.CSV', index_col=False)

saratoga_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/4114_19.CSV', index_col=False)
saratoga_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/4120_CUR.CSV', index_col=False)

# There is a typo in line 6383 of warren_14_19 source document. street_nbr cell 
# was empty from source material. . This change was updated manually in the csv file. 
warren_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/5214_19.CSV', index_col=False)
warren_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/5220_CUR.CSV', index_col=False)

washington_14_19 = pd.read_csv('Input/Real Estate Transactions/ADK/5314_19.CSV', index_col=False)
washington_20_cur = pd.read_csv('Input/Real Estate Transactions/ADK/5320_CUR.CSV', index_col=False)


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

# Creating county list for concatination 
adk_counties = [clinton_14_19, clinton_20_cur, essex_14_19, essex_20_cur,
                        franklin_14_19, frankin_20_cur, hamilton_14_19, 
                        hamilton_20_cur, herkimer_14_19, hermiker_20_cur, 
                        lewis_14_19, lewis_20_cur, oneida_14_19, oneida_20_cur,
                        st_lawrence_14_19, st_lawrence_20_cur, saratoga_14_19,
                        saratoga_20_cur, warren_14_19, warren_20_cur, 
                        washington_14_19, washington_20_cur]

#%% Appending datasets together

merged_adk_counties = pd.concat(adk_counties, ignore_index=True)
merged_adk_counties[['sale_price', 'total_av','print_key']] = merged_adk_counties[['sale_price', 'total_av','print_key']].astype(str)

#Dropping non-arms length sales baed on arms_length_flag column  

merged_adk_counties = merged_adk_counties.drop(merged_adk_counties[(merged_adk_counties['arms_length_flag'] == 'N')].index)

# creating two datasets for municipalities that contain the park 
# and non-park municipalities
 
adk_park_munis = merged_adk_counties[merged_adk_counties.muni_name.isin(adk_muni)]
non_adk_park_munis = merged_adk_counties[~merged_adk_counties.muni_name.isin(adk_muni)]

#saves to csv file.
merged_adk_counties.to_csv('Output/Real Estate/merged_adk_counties.csv')
adk_park_munis.to_csv('Output/Real Estate/adk_park_munis.csv')
non_adk_park_munis.to_csv('Output/Real Estate/non_adk_park_munis.csv')

#%% Catskill Data



#%% Catskill Real Estate Data

delaware_14_19 = pd.read_csv('Input/Real Estate Transactions/CAT/1214_19.CSV', index_col=False)
delaware_20_cur = pd.read_csv('Input/Real Estate Transactions/CAT/1220_CUR.CSV', index_col=False)

greene_14_19 = pd.read_csv('Input/Real Estate Transactions/CAT/1914_19.CSV', index_col=False)
greene_20_cur = pd.read_csv('Input/Real Estate Transactions/CAT/1920_CUR.CSV', index_col=False)

sullivan_14_19 = pd.read_csv('Input/Real Estate Transactions/CAT/4814_19.CSV', index_col=False)
sullivan_20_cur = pd.read_csv('Input/Real Estate Transactions/CAT/4820_CUR.CSV', index_col=False)

#Manually corrected two typographic errors in lines 12710 of 5114_19 and 
# line 4205 of 5120. 
ulster_14_19 = pd.read_csv('Input/Real Estate Transactions/CAT/5114_19.CSV', index_col=False)
ulster_20_cur = pd.read_csv('Input/Real Estate Transactions/CAT/5120_CUR.CSV', index_col=False)

 
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

cat_counties = [delaware_14_19, delaware_20_cur, greene_14_19, greene_20_cur, 
                sullivan_14_19, sullivan_20_cur, ulster_14_19, ulster_20_cur
                ]

#%% 
merged_cat_counties = pd.concat(cat_counties, ignore_index=True)

merged_cat_counties[['sale_price', 'total_av']] = merged_cat_counties[['sale_price', 'total_av']].apply(pd.to_numeric)

cat_park_munis = merged_cat_counties[merged_cat_counties.muni_name.isin(cat_muni)]
non_cat_park_munis = merged_cat_counties[~merged_cat_counties.muni_name.isin(cat_muni)]

#save to csv file
merged_cat_counties.to_csv('Output/Real Estate/merged_cat_counties.csv')
cat_park_munis.to_csv('Output/Real Estate/cat_park_munis.csv')
non_cat_park_munis.to_csv('Output/Real Estate/non_cat_park_munis.csv')
