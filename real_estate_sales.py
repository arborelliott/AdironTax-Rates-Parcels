# -*- coding: utf-8 -*-
"""
Created on Tue May 30 10:10:35 2023

@author: chris
"""

import pandas as pd

#%% Importing csv files. Dwnloaded all real estate transacitons from a 
#   ten year period from counties that contain the Adirondack Park. 

clinton_14_19 = pd.read_csv('Input/Real Estate Transactions/0914_19.CSV', index_col=False, )
clinton_20_cur = pd.read_csv('Input/Real Estate Transactions/0920_CUR.CSV', index_col=False)

essex_14_19 = pd.read_csv('Input/Real Estate Transactions/1514_19.CSV', index_col=False)
essex_20_cur = pd.read_csv('Input/Real Estate Transactions/1520_CUR.CSV', index_col=False)

franklin_14_19 = pd.read_csv('Input/Real Estate Transactions/1614_19.CSV', index_col=False)
frankin_20_cur = pd.read_csv('Input/Real Estate Transactions/1620_CUR.CSV', index_col=False)

fulton_14_19 = pd.read_csv('Input/Real Estate Transactions/1714_19.CSV', index_col=False)
fulton_20_cur = pd.read_csv('Input/Real Estate Transactions/1720_CUR.CSV', index_col=False)

hamilton_14_19 = pd.read_csv('Input/Real Estate Transactions/2014_19.CSV', index_col=False)
hamilton_20_cur = pd.read_csv('Input/Real Estate Transactions/2020_CUR.CSV', index_col=False)

herkimer_14_19 = pd.read_csv('Input/Real Estate Transactions/2114_19.CSV', index_col=False)
hermiker_20_cur = pd.read_csv('Input/Real Estate Transactions/2120_CUR.CSV', index_col=False)

lewis_14_19 = pd.read_csv('Input/Real Estate Transactions/2314_19.CSV', index_col=False)
lewis_20_cur = pd.read_csv('Input/Real Estate Transactions/2320_CUR.CSV', index_col=False)

oneida_14_19 = pd.read_csv('Input/Real Estate Transactions/3014_19.CSV', index_col=False)
oneida_20_cur = pd.read_csv('Input/Real Estate Transactions/3020_CUR.CSV', index_col=False)

st_lawrence_14_19 = pd.read_csv('Input/Real Estate Transactions/4014_19.CSV', index_col=False)
st_lawrence_20_cur = pd.read_csv('Input/Real Estate Transactions/4020_CUR.CSV', index_col=False)

saratoga_14_19 = pd.read_csv('Input/Real Estate Transactions/4114_19.CSV', index_col=False)
saratoga_20_cur = pd.read_csv('Input/Real Estate Transactions/4120_CUR.CSV', index_col=False)

# There is a typo in line 6383 of warren_14_19 source document. street_nbr cell 
# was empty from source material. . This change was updated manually in the csv file. 
warren_14_19 = pd.read_csv('Input/Real Estate Transactions/5214_19.CSV', index_col=False)
warren_20_cur = pd.read_csv('Input/Real Estate Transactions/5220_CUR.CSV', index_col=False)

washington_14_19 = pd.read_csv('Input/Real Estate Transactions/5314_19.CSV', index_col=False)
washington_20_cur = pd.read_csv('Input/Real Estate Transactions/5320_CUR.CSV', index_col=False)


#%% Creating a dictionary of municipalities within the park. Source:
    # https://apa.ny.gov/local_government/LGS/ADKTownsVillagesWebsites.pdf
    # Corinth through Tupper Lake are villages. 
muni = ['Altona', 'Arietta', 'AuSable', 'Bellmont', 'Benson', 'Black Brook', 
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
counties = [clinton_14_19, clinton_20_cur, essex_14_19, essex_20_cur,
                        franklin_14_19, frankin_20_cur, hamilton_14_19, 
                        hamilton_20_cur, herkimer_14_19, hermiker_20_cur, 
                        lewis_14_19, lewis_20_cur, oneida_14_19, oneida_20_cur,
                        st_lawrence_14_19, st_lawrence_20_cur, saratoga_14_19,
                        saratoga_20_cur, warren_14_19, warren_20_cur, 
                        washington_14_19, washington_20_cur]

#%% Appending datasets together

merged_counties = pd.concat(counties, ignore_index=True)
merged_counties[['sale_price', 'total_av']] = merged_counties[['sale_price', 'total_av']].apply(pd.to_numeric)

#Dropping non-arms length sales baed on arms_length_flag column  

merged_counties = merged_counties.drop(merged_counties[(merged_counties['arms_length_flag'] == 'N')].index)

# creating two datasets for municipalities that contain the park 
# and non-park municipalities
 
park_munis = merged_counties[merged_counties.muni_name.isin(muni)]
non_park_munis = merged_counties[~merged_counties.muni_name.isin(muni)]

#saves to csv file.
park_munis.to_csv('Output/Real Estate/park_munis.csv')
non_park_munis.to_csv('Output/Real Estate/non_park_munis.csv')