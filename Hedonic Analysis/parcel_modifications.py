# -*- coding: utf-8 -*-
"""
Created on Wed May 31 11:03:17 2023

@author: Rudy
"""

import geopandas as gpd
import pandas as pd
import fiona 

#Names of data files
counties_file = 'tl_2021_us_county.zip'
centroids_file = 'NYS-Tax-Parcel-Centroid-Points.gdb.zip'

#Check centroid file, retrieve sample and field names of centroid file, and get CRS of centroid file
print(fiona.listlayers(centroids_file))
main_layer = 'NYS_Tax_Parcels_All_Centroid_Points'

check = gpd.read_file(centroids_file,layer=main_layer,rows=100)
print(check.columns)

crs = check.crs
print(crs)
#%% Creating adk county masks from county file for easier reading of full centroid file

counties = gpd.read_file(counties_file)

#listing adk county names and FIPs pairs broken into separate lists
adk_counties = [
    ('Clinton','36019'),('Essex','36031'),('Franklin','36033'),('Fulton','36035'),
    ('Hamilton','36041'),('Herkimer','36043'),('Lewis','36049'),('Oneida','36065'),
    ('Saratoga','36091'),('StLawrence','36089'),('Warren','36113'),('Washington','36115')
                ]
county_name, county_FIPS = list(map(list,zip(*adk_counties))) 

#filtering county file by adk county fips
adk_shape = counties[counties['GEOID'].isin(county_FIPS)]
adk_shape = adk_shape.to_crs(crs)

#%% Reading Centroid file using adk counties as a mask to reduce load time
raw = gpd.read_file(centroids_file,layer=main_layer,mask=adk_shape)

#Filtering centroids by county name attribute for all adk county name
trim = raw[raw['COUNTY_NAME'].isin(county_name)]

#Creating a sample csv of the centroid data without geometry
adk_sample = trim.sample(n=1000,random_state=999)
adk_sample = adk_sample.drop(columns='geometry')
adk_sample.to_csv('Output/adk_centroids_sample.csv')

adk_sample_values = adk_sample['PRINT_KEY'].value_counts(dropna=False)

#%% Dropping duplicate tax parcel records
####
#The following section is how duplicates were checked and adjusted for
#Needed to look for the most unique identification code for every tax parcel 
#A combination of SWIS and PRINT_KEY codes is the most unique ID (least amount of duplicates)

#trim2 = trim.copy()                                                      #569976 records
#trim2_vals_pk = trim['PRINT_KEY'].value_counts(dropna=False)             #537809
#trim2_vals_geo = trim['geometry'].value_counts(dropna=False)             #568615 (only 1361 extras)
#trim2_vals_spk = trim['SWIS_PRINT_KEY_ID'].value_counts(dropna=False)    #568724 (only 1252 extras)
#trim2_vals_GE = trim['GRID_EAST'].value_counts(dropna=False)             #328617
#trim2_vals_GN = trim['GRID_NORTH'].value_counts(dropna=False)            #333046

#Combining Grid East and Grid North values to create unique ID's
#the resulting ID was not as unique as SWIS_PRINT_KEY_ID

#trim2 = trim2.dropna(subset=['GRID_EAST','GRID_NORTH'])                  #566599
#trim2['GRID_comb'] = trim['GRID_EAST'].map(str) + trim['GRID_NORTH'].map(str)
#trim2_vals_GC = trim2['GRID_comb'].value_counts(dropna=False)            #520957
####

#Verifying that SWIS and PRINT_KEY matches up with SWIS_PRINT_KEY_ID
#Dropping missing values of SWIS and PRINT_KEY and checking duplicated values
trim['SWIS_comb'] = trim['SWIS'] + trim['PRINT_KEY']
equals = trim['SWIS_comb'].equals(trim['SWIS_PRINT_KEY_ID'])

trim_vals = trim['SWIS_comb'].value_counts(dropna=False)                 #568724 (only 1252 extras)
trim = trim.drop(columns='SWIS_comb')

trim_dups = trim.dropna(subset=['PRINT_KEY','SWIS'])                     #568739
is_dup = trim_dups.duplicated(subset=['PRINT_KEY','SWIS'],keep=False)
trim_dups = trim_dups[is_dup]                                            #30 records that are duplicates
trim_dups_vals = trim_dups['SWIS_PRINT_KEY_ID'].value_counts()           #14 IDs with duplicates

#Removing duplicates by selecting the last entry and missing values
trim = trim.drop_duplicates(subset='SWIS_PRINT_KEY_ID',keep='last')
trim = trim.dropna(subset='SWIS_PRINT_KEY_ID')

print(trim['SWIS_PRINT_KEY_ID'].value_counts())
#%% Stripping and exporting centroid data into geospatial file and data attribute file for easier handling

trim_geo = trim[['SWIS_PRINT_KEY_ID','geometry']]
trim_geo.to_file('Output/parcels.gpkg',layer='adk_counties')

trim_data = trim.loc[:,trim.columns!='geometry']
trim_data.to_csv('Output/Centroid_parcels_data.csv',index=False)
trim_data.to_pickle('Output/Centroid_parcels_data.zip')

trim3 = pd.read_pickle('Output/Centroid_parcels_data.zip')
equals2 = trim_data.equals(trim3)

trim2 = pd.read_csv('Output/Centroid_parcels_data.csv',dtype=str)
equals = trim_data.astype(str).equals(trim2)


#%%#Filtering centroids for each adk county separately and exporting result as a layer in a geopackage
#Script will print confirmation for completion of each county centroid layer

def filt_exp(county):
    filtered = trim[trim['COUNTY_NAME']==county]
    filtered.to_file('Output/parcels.gpkg',layer=f'{county}_centroids')
    return filtered

Clinton = filt_exp('Clinton')
print('Clinton done')

Essex = filt_exp('Essex')
print('Essex done')

Franklin = filt_exp('Franklin')
print('Franklin done')

Fulton = filt_exp('Fulton')
print('Fulton done')

Hamilton = filt_exp('Hamilton')
print('Hamilton done')

Herkimer = filt_exp('Herkimer')
print('Herkimer done')

Lewis = filt_exp('Lewis')
print('Lewis done')

Oneida = filt_exp('Oneida')
print('Oneida done')

Saratoga = filt_exp('Saratoga')
print('Saratoga done')

StLawrence = filt_exp('StLawrence')
print('StLawrence done')

Warren = filt_exp('Warren')
print('Warren done)')

Washington = filt_exp('Washington')
print('Washington done')

