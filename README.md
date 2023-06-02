# ADK_Census_data
 
 Order of operations
1. ## **Boundaries_Merge.py**: 1st

    This script combines boundary data from 2 seperate data sets (town and city) and (villages) Combined the data set has all three. 
    The main purpose is to match NY SWIS codes to Census FIPS Codes
    This Script outputs NYS_Tax_rates_Levy_Roll21.csv which contains data on tax rates throughout the state, 
    which is used for the next script Parcel_tax_Merge_func.py
    
    INPUT: 
        NYS_Civil_Boundaries_TOWN_CITY.csv
        NYS_Civil_Boundaries_VILLAGES.csv - Civil boundary data from NYS GIS
        Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv - Historical Tax rate data for NYS

    OUTPUT: 
        NYS_Tax_rates_Levy_Roll21.csv - Tax rates for 2021, With SWIS and FIPS codes

    VARIABLES:
        - Year of tax rates (default 2021)

2. ## **Census_API.py**: 2nd, Run after Boundaries_merge.py
    This script runs a function which retrieves information from the Census API 
    based on desired geographic regions within NY.

    INPUT: 
        Data received from census API Request

    OUTPUT: 
        Census information is exported to Output/Census/... to be used in later scripts. 
        Naming based on geographic area of census
        
    VARIABLES: 
        retrieve_census(for_clause, title)
    choose the geographic location desired in the census, and the title you want to be attached to the outputs. 

    **Useful Links**
    https://api.census.gov/data/2020/acs/acs5/variables.html
    https://api.census.gov/data/2020/acs/acs5/geography.html


3. Parcel_tax_Merge_func.py
This script imports tax rate data from the previous script, and parcel data from assessment rolls. 

The Script cleans the data, subsets to a given year and property class, and merges the parcel data with the tax rate data to calculate the amount of taxes paid on each parcel. 

The script outputs 3 graphs per region of interest, and an excel file summarizing the findings. 

Hedonic Analysis Inputs
https://drive.google.com/drive/u/1/folders/1L8UAh_Wk8CmldDZbjkQG0p5GPbFtZ3Hq
