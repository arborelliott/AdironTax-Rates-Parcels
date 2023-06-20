# ADK_Census_data
 
 Order of operations
1. ## **Boundaries_Merge.py**: 1st

    This script combines boundary data from 2 seperate data sets (town and city) and (villages) Combined the data set has all three. 
    The main purpose is to match NY SWIS codes to Census FIPS Codes
    This Script outputs NYS_Tax_rates_Levy_Roll21.csv which contains data on tax rates throughout the state, 
    which is used for the next script Parcel_tax_Merge_func.py
    
    **INPUT:**

    1. NYS_Civil_Boundaries_TOWN_CITY.csv: 
    [Source](https://data.gis.ny.gov/maps/nys-civil-boundaries/about)
    
    2. NYS_Civil_Boundaries_VILLAGES.csv: Civil boundary data from NYS GIS:
    [Source](https://data.gis.ny.gov/maps/nys-civil-boundaries/about)
    
    3. Real_Property_Tax_Rates_Levy_Data_By_Municipality__Beginning_2004.csv: Historical Tax rate data for NYS
    [Source](https://data.ny.gov/Government-Finance/Real-Property-Tax-Rates-Levy-Data-By-Municipality-/iq85-sdzs)

    **OUTPUT:**

     NYS_Tax_rates_Levy_Roll21.csv - Tax rates for 2021, With SWIS and FIPS codes

    **VARIABLES:**

    Year of tax rates (default 2021)

2. ## **Census_API.py**: 2nd, 

    Run after Boundaries_merge.py

    This script runs a function which retrieves information from the Census API 
    based on desired geographic regions within NY.

    Please note that the user-specific Census API key was removed from the script: census_api. A new code will need to be added for it to function. 

    **INPUT:**
        
    Data received from census API Request

    **OUTPUT:** 
       
    Census information is exported to Output/Census/... to be used in later scripts. 
        Naming based on geographic area of census

    **VARIABLES:** 
       
    retrieve_census(for_clause, title) choose the geographic location desired in the census, and the title you want to be attached to the outputs. 

    **Useful Links**

     https://api.census.gov/data/2020/acs/acs5/variables.html

    https://api.census.gov/data/2020/acs/acs5/geography.html


3. ## Parcel_tax_Merge.py: 3rd

    This should be run after Boundaries_Merge and census_api
    This script imports tax rate data from the previous script, and parcel data from assessment rolls. 
    The Script cleans the data, subsets to a given year and property class, and merges the parcel data with the tax rate data to calculate the amount of taxes paid on each parcel. 
    The script outputs 3 graphs per region of interest, and an excel file summarizing the findings.  
    
    **INPUT:**
    
    1. NYS_Tax_rates_Levy_Roll21.csv (From Boundaries_Merge.py)
        
    2. Property_Assessment_Data_from_Local_Assessment_Rolls_931_980_940_932_990.csv: Assessment rolls from NYS [Source](https://data.ny.gov/Government-Finance/Property-Assessment-Data-from-Local-Assessment-Rol/7vem-aaz7)
        
    3. Census data (From Census_api), ex: Census/County_Census.xlsx

    **OUTPUT:**

    {taxcode}_{prefix}_parcel_tax.xlsx - Summary of state tax expenditure by locality. 
        
    **VARIABLES:**
    
    1. Property class
    2. Tax year

    Hedonic Analysis Inputs
    https://drive.google.com/drive/u/1/folders/1L8UAh_Wk8CmldDZbjkQG0p5GPbFtZ3Hq

4. ## Hedonic_SCT_Merge.py: 4th

    This script merges together three other primary data sets: sales, Centroids, and tax information. The output is the centroids data set with sales associated to applicable parcels, and tax data applied to ADK localities. This output was designed specifically to conduct the hedonic analysis

    **INPUT:**

    1. merged_adk_counties_10k.csv (From Read_estate_sales.py): Sales data for ADK parcels, sold for over 10k.

    2. Centroid_parcels_data.zip: Parcel centroid data for NYS

    3. {taxcode}_{prefix}_parcel_tax.xlsx (From Parcel_Tax_Merge.py): Data on tax received for each locality in either ADK or CAT

    **OUTPUT:**
    
    {taxcode}_{prefix}_Hedonic_ana_sct.csv: Output for Hedonic analysis
        
        
    **VARIABLES:**
        
    Pclass: Specify property code desired
    Prefix: Specify prefix if imported and exported data

        
## Other Scripts

    Village Calculations.py - This script analyzes parcel data in a similar way to parcel_tax_merge, however for villages only. This script should be run after the first 3 scripts and generates summary tables in the Outputs folder. 

    Hedonic Analysis scripts (folder) - these scripts were used to conduct the hedonic analysis, and may be useful for future work on this topic or replication of the analysis. 