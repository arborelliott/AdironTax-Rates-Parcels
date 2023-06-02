# -*- coding: utf-8 -*-
"""
Created on Wed May 31 11:03:17 2023

@author: Rudy
"""

import geopandas as gpd
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
#%%Creating adk county masks from county file for easier reading of full centroid file

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

#%%Reading Centroid file using adk counties as a mask to reduce load time
raw = gpd.read_file(centroids_file,layer=main_layer,mask=adk_shape)

#Filtering centroids by county name attribute for all adk county name
trim = raw[raw['COUNTY_NAME'].isin(county_name)]

adk_sample = trim.sample(n=1000,random_state=999)
adk_sample = adk_sample.drop(columns='geometry')
adk_sample.to_csv('Outputs/adk_centroids_sample.csv')

#Filtering centroids for each adk county separately and exporting result as a layer in a geopackage
#Script will print confirmation for completion of each county centroid layer

def filt_exp(county):
    filtered = trim[trim['COUNTY_NAME']==county]
    filtered.to_file('Outputs/parcels.gpkg',layer=f'{county}_centroids')
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

