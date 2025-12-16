"""
This module provides functions to load and preprocess Shopify and Amazon data, including standardizing addresses and splitting full names.

Functions:
- load_shopify_data(): Loads and preprocesses Shopify data from a CSV file.
- load_amazon_data(path=None): Loads and preprocesses Amazon data from a CSV file.

load_shopify_data():
    Loads and preprocesses Shopify data from a CSV file.

    Steps:
    1. Load data from 'data_science/shopify_emails.csv'.
    2. Convert column names to lowercase.
    3. Convert specified date columns to datetime.
    4. Split 'full_name' into 'first_name', 'middle_name', and 'last_name'.
    5. Convert name columns to uppercase and create 'middle_initial'.
    6. Standardize addresses.
    7. Save cleaned data to 'TEMP_shopify_clean.csv'.

    Returns:
        pd.DataFrame: Preprocessed Shopify data.

load_amazon_data(path=None):
    Loads and preprocesses Amazon data from a CSV file.

    Steps:
    1. Load data from 'data_science/amazon_emails.csv' or specified path.
    2. Convert column names to lowercase and rename columns.
    3. Split 'full_name' into 'first_name', 'middle_name', and 'last_name'.
    4. Convert name columns to uppercase and create 'middle_initial'.
    5. Map country names to codes and clean state/zip codes.
    6. Standardize addresses.
    7. Save cleaned data to 'TEMP_amazon_clean.csv'.

    Args:
        path (str, optional): File path to the Amazon data CSV file. Defaults to None.

    Returns:
        pd.DataFrame: Preprocessed Amazon data.
"""

import pandas as pd
import numpy as np
import string
from data_science.address_utils import standardize_address_amazon
from data_science.address_utils import standardize_address_shopify
from data_science.address_utils import standardize_address_netsuite
from data_science.address_utils import split_full_name
from data_science.address_utils import state_to_country
from tqdm import tqdm
import hashlib


tqdm.pandas()

def load_shopify_data(path=None, test=False, use_cache=False):
    # https://app.snowflake.com/loracbl/ilb81531/wZERO5Cnsuu#query

    if use_cache:
        try:
            return pd.read_csv('TEMP_shopify_clean.csv').fillna('')
        except FileNotFoundError:
            pass
    
    # Load Shopify data
    if path is None:
        file_path = 'data_science/shopify_emails.csv'
    else:
        file_path = path

    shopify_data = pd.read_csv(file_path)

    # Convert column names to lowercase
    shopify_data.columns = shopify_data.columns.str.lower()

    if test:
        shopify_data = shopify_data.sample(frac=0.05)

    # List of columns to convert to datetime
    date_columns = [
        'first_order_date', 
        'latest_order_date', 
        'latest_subscription_start_date', 
        'latest_subscription_cancel_date'
    ]

    # Convert date columns to pandas datetime
    for col in date_columns:
        shopify_data[col] = pd.to_datetime(shopify_data[col], errors='coerce')

    # Function to split full_name into first, middle, and last names
    # Apply the function to the full_name column
    print('Running shopify name recognition')
    shopify_data[['first_name', 'middle_name', 'last_name']] = shopify_data['full_name'].fillna('').progress_apply(
        lambda x: pd.Series(split_full_name(x))
    )

    # Convert first_name, middle_name, and last_name to uppercase
    shopify_data['first_name'] = shopify_data['first_name'].str.upper()
    shopify_data['middle_name'] = shopify_data['middle_name'].str.upper()
    shopify_data['last_name'] = shopify_data['last_name'].str.upper()

    # Create a middle_initial column
    shopify_data['middle_initial'] = shopify_data['middle_name'].str[0]

    # ✅ Create Shopify DataFrame
    df_shopify = pd.DataFrame(shopify_data)

    print('Running shopify address tokenization')
    # ✅ Apply standardize_address with tqdm progress bar
    standardized_df = df_shopify.progress_apply(
        lambda row: pd.Series(standardize_address_shopify(row.fillna('').astype(str))),
        axis=1
    )

    # ✅ Combine original DataFrame with standardized data, keeping only standardized_df columns in case of duplicates
    df_shopify = df_shopify.drop(columns=standardized_df.columns, errors='ignore')
    df_shopify = pd.concat([df_shopify, standardized_df], axis=1)

    # Drop rows where all standardized address fields are null
    df_shopify = df_shopify.dropna(subset=[
        'address_number', 'street_name', 'street_type', 'unit_type', 'unit_number',
        'city', 'state', 'state_code', 'country', 'country_code', 'zip', 'zip_cleaned'
    ], how='all')

    df_shopify['shopify_id'] = df_shopify['customer_id'] # just for match algo cleanliness

    if not test:
        df_shopify.to_csv('TEMP_shopify_clean.csv', index=False)

    return df_shopify


def load_amazon_data(path=None, test=False):
    # Load Amazon data
    if path is None: 
        file_path = 'data_science/amazon_emails.csv'
    else: 
       file_path = path


    amazon_data = pd.read_csv(file_path)

    if test: 
        amazon_data = amazon_data.sample(frac=0.05)

    # Convert column names to lowercase
    amazon_data.columns = amazon_data.columns.str.lower()

    amazon_data.columns = [
        'provider', 
        'order_id',
        'order_date',
        'first_name',
        'last_name',   
        'full_name',
        'email_amzn',
        'address', 
        'city', 
        'state', 
        'zip', 
        'country',
        'skus', 
        'qty', 
        'sku', 
        'subtotals'
    ]



    # Function to split full_name into first, middle, and last names
    amazon_data[['first_name', 'middle_name', 'last_name']] = amazon_data['full_name'].astype('str').progress_apply(
        lambda x: pd.Series(split_full_name(x))
    )
    
    print('Running amazon name recognition')
    # Convert first_name, middle_name, and last_name to uppercase
    amazon_data['first_name'] = amazon_data['first_name'].str.upper()
    amazon_data['middle_name'] = amazon_data['middle_name'].str.upper()
    amazon_data['last_name'] = amazon_data['last_name'].str.upper()

    # Create a middle_initial column
    amazon_data['middle_initial'] = amazon_data['middle_name'].str[0]

    # Dictionary to map country names to country codes
    country_mapping = {
        'US': 'US',
        'United States': 'US',
        'CA': 'CA',
        'British Columbia': 'CA',
        'Canada': 'CA',
        'New Zealand': 'NZ',
        'Hong Kong (SAR)': 'HK',
        'United Arab Emirates': 'AE',
        'Indonesia': 'ID',
        'United States Minor Outlying Island': 'UM'
    }

    # Convert country names to country codes
    amazon_data['country_code'] = amazon_data['country'].map(country_mapping)

    # Drop rows where country_code is NaN (i.e., countries not in the mapping)
    amazon_data = amazon_data.dropna(subset=['country_code'])

    # ✅ Create Amazon DataFrame
    df_amazon = pd.DataFrame(amazon_data)

    # Clean up to work cleanly with Amazon data
    df_amazon['state_code'] = df_amazon['state'].str.upper()
    # Remove rows where state_code is null or not a 2-letter string when country_code is 'US'
    df_amazon = df_amazon[~((df_amazon['country_code'] == 'US') & 
                            ((df_amazon['state_code'].isnull()) | 
                             (df_amazon['state_code'].str.len() != 2)))]

    # Isolate zip to the first 5 digits and create a new column 'zip_cleaned' only when country_code = 'US'
    df_amazon['zip_cleaned'] = df_amazon.apply(
        lambda row: row['zip'][:5] if row['country_code'] == 'US' else row['zip'], axis=1
    )
    # Standardize Canadian zip codes
    def standardize_canadian_zip(zip_code):
        # Remove spaces and special characters
        standardized_zip = ''.join(e for e in zip_code if e.isalnum())
        # Ensure it is a 6 character string
        if len(standardized_zip) == 6:
            return standardized_zip
        else:
            return np.nan

    # Apply the standardization function to Canadian zip codes
    df_amazon['zip_cleaned'] = df_amazon.apply(
        lambda row: standardize_canadian_zip(row['zip']) if row['country_code'] == 'CA' else row['zip_cleaned'], axis=1
    )

    # Drop rows with invalid Canadian zip codes
    df_amazon = df_amazon[~((df_amazon['country_code'] == 'CA') & (df_amazon['zip_cleaned'].isnull()))]
    
    # Drop rows where order_date or full_name is NaN
    df_amazon = df_amazon.dropna(subset=['order_date', 'full_name']) # this data is useless

    df_amazon = df_amazon.fillna('') # String coercion 

    print('Running amazon address tokenization')
    # ✅ Apply standardize_address with tqdm progress bar
    standardized_df = df_amazon.progress_apply(
        lambda row: pd.Series(standardize_address_amazon(row.astype(str))),
        axis=1
    )

    # ✅ Combine original DataFrame with standardized data, keeping only standardized_df columns in case of duplicates
    df_amazon = df_amazon.drop(columns=standardized_df.columns, errors='ignore')
    df_amazon = pd.concat([df_amazon, standardized_df], axis=1)

    # Drop rows where all standardized address fields are null
    df_amazon = df_amazon.dropna(subset=[
        'address_number', 'street_name', 'street_type', 'unit_type', 'unit_number',
        'city', 'state', 'state_code', 'country', 'country_code', 'zip', 'zip_cleaned'
    ], how='all')

    def generate_amazon_id(row):
        # Concatenate the relevant fields
        data = f"{row['full_name']}_{row['order_date']}_{row['zip_cleaned']}"
        # Generate a hash of the concatenated string
        return hashlib.sha256(data.encode()).hexdigest()

    # Generate a unique amazon_id using full_name, order_date, and zip_cleaned
    df_amazon['amazon_id'] = df_amazon.apply(generate_amazon_id, axis=1)

    if not test:
        df_amazon.to_csv('TEMP_amazon_clean.csv', index=False)
    
    return df_amazon


def load_netsuite_data(path, test=False): 
    print('loading latest netsuite data from file {}'.format(path))   
    netsuite = pd.read_csv(path)
    netsuite.columns = [
        'internal_id',
        'date',
        'document_number', 
        'order_name', 
        'address_1', 
        'address_2', 
        'city',
        'state', 
        'zip'   
    ]

    netsuite = netsuite.replace(
        '(blank)', ''
    )

    netsuite['country_code'] = netsuite['state'].map(state_to_country)

        # Step 1: Isolate U.S. zip codes to first 5 digits
    netsuite['zip_cleaned'] = netsuite.apply(
        lambda row: row['zip'][:5] if row['country_code'] == 'US' and isinstance(row['zip'], str) else row['zip'],
        axis=1
    )

    # Step 2: Define Canadian zip standardization
    def standardize_canadian_zip(zip_code):
        if not isinstance(zip_code, str):
            return np.nan
        # Remove spaces and special characters
        standardized_zip = ''.join(e for e in zip_code if e.isalnum())
        # Ensure it's a 6-character alphanumeric string
        return standardized_zip if len(standardized_zip) == 6 else np.nan

    # Step 3: Apply to Canadian zips
    netsuite['zip_cleaned'] = netsuite.apply(
        lambda row: standardize_canadian_zip(row['zip']) if row['country_code'] == 'CA' else row['zip_cleaned'],
        axis=1
    )

    print('Running netsuite address tokenization')
    # ✅ Apply standardize_address with tqdm progress bar
    standardized_df = netsuite.progress_apply(
        lambda row: pd.Series(standardize_address_netsuite(row.astype(str))),
        axis=1
    )

        # ✅ Combine original DataFrame with standardized data, keeping only standardized_df columns in case of duplicates
    netsuite = netsuite.drop(columns=standardized_df.columns, errors='ignore')
    netsuite = pd.concat([netsuite, standardized_df], axis=1)

    # Drop rows where all standardized address fields are null
    netsuite = netsuite.dropna(subset=[
        'address_number', 'street_name', 'street_type', 'unit_type', 'unit_number',
        'city', 'state', 'state_code', 'country', 'country_code', 'zip', 'zip_cleaned'
    ], how='all')

    # Confusing, but just done to make rest of match algorithm work correctly
    netsuite['amazon_id'] = netsuite['internal_id'] # just for match algo cleanliness

    if not test:
        netsuite.to_csv('TEMP_netsuite_clean.csv', index=False)

    return netsuite



    
    


    
    
    



