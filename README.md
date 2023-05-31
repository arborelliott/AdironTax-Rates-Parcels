# ADK_Census_data
 
 Order of operations
1. Boundaries_Merge.py
This script combines boundry data from 2 seperate data sets (town and city) and (villages) Combined the data set has all three. The main purpose is to match NY SWIS codes to Census FIPS Codes

This Script outputs NYS_Tax_rates_Levy_Roll21.csv which contains data on tax rates throughout the state, which is used for the next script Parcel_tax_Merge_func.py

2. Census API
This script runs a function which retrieves information from the Census API based on desired geographic regions within NY.
Census information is exported to Output/Census/...



3. Parcel_tax_Merge_func.py
This script imports tax rate data from the previous script, and parcel data from assessment rolls. 

The Script cleans the data, subsets to a given year and property class, and merges the parcel data with the tax rate data to calculate the amount of taxes paid on each parcel. 

The script outputs 3 graphs per region of interest, and an excel file summarizing the findings. 