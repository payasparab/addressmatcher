"""
normalize_house_number(num):
    Normalizes house numbers by removing non-numeric characters and converting to string.
        num (str or int or float): The house number to normalize.
        str: The normalized house number as a string.
This module provides utilities for parsing and standardizing addresses, as well as splitting full names.
Attributes:
    street_type_mapping (dict): A dictionary mapping various street type names to their standardized abbreviations.
    matchable_columns (list): A list of columns that are applicable across both standardized and cleaned up addresses from Amazon and Shopify.
Functions:
    parse_us_address(address):
        Parses a US address using the usaddress library.
        Args:
            address (str): The address to parse.
        Returns:
            dict: A dictionary containing the parsed address components.
    parse_international_address(address):
        Parses an international address using the pyap library.
        Args:
            address (str): The address to parse.
        Returns:
            dict: A dictionary containing the parsed address components, or an empty dictionary if parsing fails.
    standardize_address_shopify(row):
        Standardizes a Shopify address, converting street types to their standardized abbreviations and converting all text to uppercase.
        Args:
            row (pd.Series): A pandas Series containing the address components.
        Returns:
            pd.Series: A pandas Series containing the standardized address components.
    standardize_address_amazon(row):
        Standardizes an Amazon address, converting street types to their standardized abbreviations and converting all text to uppercase.
        Args:
            row (pd.Series): A pandas Series containing the address components.
        Returns:
            pd.Series: A pandas Series containing the standardized address components.
    split_full_name(full_name):
        Splits a full name into first, middle, and last names, removing any punctuation.
        Args:
            full_name (str): The full name to split.
        Returns:
            pd.Series: A pandas Series containing the first, middle, and last names.
"""
import pandas as pd
import usaddress
import pyap
import string

# Mapping for standardizing street types
street_type_mapping = {
    'STREET': 'ST',
    'ST': 'ST',
    'ST.': 'ST',
    'AVENUE': 'AVE',
    'AVE': 'AVE',
    'AVE.': 'AVE',
    'BOULEVARD': 'BLVD',
    'BLVD': 'BLVD',
    'BLVD.': 'BLVD',
    'ROAD': 'RD',
    'RD': 'RD',
    'RD.': 'RD',
    'DRIVE': 'DR',
    'DR': 'DR',
    'DR.': 'DR',
    'COURT': 'CT',
    'CT': 'CT',
    'CT.': 'CT',
    'LANE': 'LN',
    'LN': 'LN',
    'LN.': 'LN',
    'TERRACE': 'TER',
    'TER': 'TER',
    'TER.': 'TER',
    'PLACE': 'PL',
    'PL': 'PL',
    'PL.': 'PL',
    'SQUARE': 'SQ',
    'SQ': 'SQ',
    'SQ.': 'SQ',
    'TRAIL': 'TRL',
    'TRL': 'TRL',
    'TRL.': 'TRL',
    'PARKWAY': 'PKWY',
    'PKWY': 'PKWY',
    'PKWY.': 'PKWY',
    'COMMONS': 'CMNS',
    'CMNS': 'CMNS',
    'CMNS.': 'CMNS',
    'HIGHWAY': 'HWY',
    'HWY': 'HWY',
    'HWY.': 'HWY',
    'CIRCLE': 'CIR',
    'CIR': 'CIR',
    'CIR.': 'CIR',
    'EXPRESSWAY': 'EXPY',
    'EXPY': 'EXPY',
    'EXPY.': 'EXPY'
}

matchable_columns = [
    'first_name',
    'middle_name',
    'middle_initial',
    'last_name',
    'full_name',
    'city',
    'state',
    'state_code',
    'country',
    'country_code',
    'zip',
    'zip_cleaned',
    'address_number',
    'street_name',
    'street_type',
    'unit_type',
    'unit_number'
]

# Function to parse US addresses
def parse_us_address(address):
    try:
        parsed = usaddress.tag(address)[0]
    except usaddress.RepeatedLabelError as e:
        parsed = {}
    return parsed

# Function to parse International addresses
def parse_international_address(address):
    parsed_addresses = pyap.parse(address, country='GB')  # Adjust country as needed
    if parsed_addresses:
        return parsed_addresses[0].as_dict()
    else:
        return {}

# ✅ Function to standardize addresses, street types, and convert to ALL CAPS
def standardize_address_shopify(row):
    try:
        if row['country_code'].upper() == 'US':
            parsed = parse_us_address(row['full_address'])
            
            # Standardize street type using mapping
            street_type = parsed.get('StreetNamePostType', '').upper().strip()
            standardized_street_type = street_type_mapping.get(street_type, street_type)

            return pd.Series({
                'address_number': normalize_house_number(parsed.get('AddressNumber', '').strip()),
                'street_name': parsed.get('StreetName', '').upper().strip() if parsed.get('StreetName') else None,
                'street_type': standardized_street_type,
                'unit_type': parsed.get('OccupancyType', '').upper().strip() if parsed.get('OccupancyType') else None,
                'unit_number': parsed.get('OccupancyIdentifier', '').upper().strip() if parsed.get('OccupancyIdentifier') else None,
                'city': parsed.get('PlaceName', row['city']).upper().strip() if parsed.get('PlaceName') else row['city'].upper().strip(),
                'state': parsed.get('StateName', row['state']).upper().strip() if parsed.get('StateName') else row['state'].upper().strip(),
                'state_code': parsed.get('StateName', row['state_code']).upper().strip() if parsed.get('StateName') else row['state_code'].upper().strip(),
                'country': row['country'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('ZipCode', row['zip']).upper().strip() if parsed.get('ZipCode') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })
        else:
            parsed = parse_international_address(row['full_address'])
            return pd.Series({
                'address_number': normalize_house_number(parsed.get('AddressNumber', '').strip()),
                'street_name': parsed.get('street_name', '').upper().strip() if parsed.get('street_name') else None,
                'street_type': None,  # Adjust if needed for international addresses
                'unit_type': None,
                'unit_number': None,
                'city': parsed.get('city', row['city']).upper().strip() if parsed.get('city') else row['city'].upper().strip(),
                'state': None,
                'state_code': None,
                'country': row['country'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('postal_code', row['zip']).upper().strip() if parsed.get('postal_code') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })
    except Exception as e:
        return pd.Series({
            'address_number': None,
            'street_name': None,
            'street_type': None,
            'unit_type': None,
            'unit_number': None,
            'city': None,
            'state': None,
            'state_code': None,
            'country': None,
            'country_code': None,
            'zip': None,
            'zip_cleaned': None
        })

def standardize_address_amazon(row):
    try:
        if row['country_code'].upper() == 'US':
            parsed = parse_us_address(row['address'])
            
            # Standardize street type using mapping
            street_type = parsed.get('StreetNamePostType', '').upper()
            standardized_street_type = street_type_mapping.get(street_type, street_type)

            return pd.Series({
                'address_number': parsed.get('AddressNumber', '').upper().strip() if parsed.get('AddressNumber') else None,
                'street_name': parsed.get('StreetName', '').upper().strip() if parsed.get('StreetName') else None,
                'street_type': standardized_street_type.strip() if standardized_street_type else None,
                'unit_type': parsed.get('OccupancyType', '').upper().strip() if parsed.get('OccupancyType') else None,
                'unit_number': parsed.get('OccupancyIdentifier', '').upper().strip() if parsed.get('OccupancyIdentifier') else None,
                'city': parsed.get('PlaceName', row['city']).upper().strip() if parsed.get('PlaceName') else row['city'].upper().strip(),
                'state': parsed.get('StateName', row['state']).upper().strip() if parsed.get('StateName') else row['state'].upper().strip(),
                'state_code': parsed.get('StateName', row['state_code']).upper().strip() if parsed.get('StateName') else row['state_code'].upper().strip(),
                'country': row['country'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('ZipCode', row['zip']).upper().strip() if parsed.get('ZipCode') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })
        else:
            parsed = parse_international_address(row['address'])
            return pd.Series({
                'address_number': parsed.get('street_number', '').upper().strip() if parsed.get('street_number') else None,
                'street_name': parsed.get('street_name', '').upper().strip() if parsed.get('street_name') else None,
                'street_type': None,  # Adjust if needed for international addresses
                'unit_type': None,
                'unit_number': None,
                'city': parsed.get('city', row['city']).upper().strip() if parsed.get('city') else row['city'].upper().strip(),
                'state': None,
                'state_code': None,
                'country': row['country'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('postal_code', row['zip']).upper().strip() if parsed.get('postal_code') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })
    except Exception as e:
        return pd.Series({
            'address_number': None,
            'street_name': None,
            'street_type': None,
            'unit_type': None,
            'unit_number': None,
            'city': None,
            'state': None,
            'state_code': None,
            'country': None,
            'country_code': None,
            'zip': None,
            'zip_cleaned': None
        })

def standardize_address_netsuite(row):
    try:
        # Combine address_1 and address_2, with a comma for better parsing
        full_address = f"{row['address_1']}, {row['address_2']}".strip(', ')

        if row['country_code'].upper() == 'US':
            parsed = parse_us_address(full_address)

            street_type = parsed.get('StreetNamePostType', '').upper()
            standardized_street_type = street_type_mapping.get(street_type, street_type)

            return pd.Series({
                'address_number': parsed.get('AddressNumber', '').upper().strip() if parsed.get('AddressNumber') else None,
                'street_name': parsed.get('StreetName', '').upper().strip() if parsed.get('StreetName') else None,
                'street_type': standardized_street_type.strip() if standardized_street_type else None,
                'unit_type': parsed.get('OccupancyType', '').upper().strip() if parsed.get('OccupancyType') else None,
                'unit_number': parsed.get('OccupancyIdentifier', '').upper().strip() if parsed.get('OccupancyIdentifier') else None,
                'city': parsed.get('PlaceName', row['city']).upper().strip() if parsed.get('PlaceName') else row['city'].upper().strip(),
                'state': parsed.get('StateName', row['state']).upper().strip() if parsed.get('StateName') else row['state'].upper().strip(),
                'state_code': parsed.get('StateName', row['state']).upper().strip() if parsed.get('StateName') else row['state'].upper().strip(),
                'country': row['country_code'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('ZipCode', row['zip']).upper().strip() if parsed.get('ZipCode') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })

        else:
            # Handle international addresses
            parsed = parse_international_address(full_address)

            return pd.Series({
                'address_number': parsed.get('street_number', '').upper().strip() if parsed.get('street_number') else None,
                'street_name': parsed.get('street_name', '').upper().strip() if parsed.get('street_name') else None,
                'street_type': None,
                'unit_type': None,
                'unit_number': None,
                'city': parsed.get('city', row['city']).upper().strip() if parsed.get('city') else row['city'].upper().strip(),
                'state': None,
                'state_code': None,
                'country': row['country_code'].upper().strip(),
                'country_code': row['country_code'].upper().strip(),
                'zip': parsed.get('postal_code', row['zip']).upper().strip() if parsed.get('postal_code') else row['zip'].upper().strip(),
                'zip_cleaned': row['zip_cleaned'].upper().strip() if row['zip_cleaned'] else None
            })

    except Exception as e:
        return pd.Series({
            'address_number': None,
            'street_name': None,
            'street_type': None,
            'unit_type': None,
            'unit_number': None,
            'city': None,
            'state': None,
            'state_code': None,
            'country': None,
            'country_code': None,
            'zip': None,
            'zip_cleaned': None
        })

    
def split_full_name(full_name):
    # Remove punctuation from the full name
    full_name = full_name.translate(str.maketrans('', '', string.punctuation))
    parts = full_name.split()
    # ✅ Handle empty names
    if len(parts) == 0:
        return pd.Series(['', '', ''])
    if len(parts) == 1:
        return pd.Series([parts[0], '', ''])
    elif len(parts) == 2:
        return pd.Series([parts[0], '', parts[1]])
    elif len(parts) == 3:
        return pd.Series([parts[0], parts[1], parts[2]])
    else:
        return pd.Series([parts[0], ' '.join(parts[1:-1]), parts[-1]])
    

def normalize_house_number(num):
    """Normalize house numbers by removing non-numeric characters and converting to string"""
    if pd.isna(num) or str(num).strip() == '':
        return ''
    num_str = str(num).replace(' ', '')
    if not num_str.isdigit():
        return num_str
    return str(float(num_str)).rstrip('0').rstrip('.')

state_to_country = {
    # United States (US)
    'TX': 'US', 'CA': 'US', 'FL': 'US', 'NY': 'US', 'OH': 'US', 'PA': 'US', 'IL': 'US', 'NC': 'US',
    'MI': 'US', 'VA': 'US', 'GA': 'US', 'MA': 'US', 'TN': 'US', 'IN': 'US', 'NJ': 'US', 'WI': 'US',
    'MN': 'US', 'WA': 'US', 'MD': 'US', 'SC': 'US', 'MO': 'US', 'KY': 'US', 'AZ': 'US', 'AL': 'US',
    'CT': 'US', 'OK': 'US', 'CO': 'US', 'KS': 'US', 'IA': 'US', 'OR': 'US', 'MS': 'US', 'AR': 'US',
    'LA': 'US', 'NE': 'US', 'NH': 'US', 'WV': 'US', 'ME': 'US', 'NV': 'US', 'NM': 'US', 'UT': 'US',
    'MT': 'US', 'ND': 'US', 'SD': 'US', 'ID': 'US', 'RI': 'US', 'VT': 'US', 'DE': 'US', 'WY': 'US',
    'AK': 'US', 'HI': 'US', 'DC': 'US', 'PR': 'US',

    # Canada (CA)
    'ON': 'CA', 'QC': 'CA', 'AB': 'CA', 'BC': 'CA', 'MB': 'CA', 'NB': 'CA', 'NS': 'CA',
    'PE': 'CA', 'SK': 'CA', 'NL': 'CA', 'NT': 'CA', 'NU': 'CA', 'YT': 'CA',
    'Newfoundland': 'CA', 'Yukon': 'CA', 'Nouveau-Brunswick': 'CA', 'Northwest Territories': 'CA',

    # Unknown or missing
    '': None
}
