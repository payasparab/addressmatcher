import pandas as pd
from data_science.address_utils import matchable_columns
from tqdm import tqdm 
from fuzzywuzzy import fuzz

# Default weights (Sum = 1.0 without zip_cleaned)
default_weights = {
    'last_name': 0.25,
    'unit_number': 0.18,
    'street_name': 0.18,
    'house_number': 0.15,
    'state': 0.05,
    'first_name': 0.04,
    'city': 0.03,
    'street_type': 0.03,
    'unit_type': 0.03
}

no_name_weights = {
    'unit_number': 0.2381,
    'street_name': 0.2381,
    'house_number': 0.1905,
    'state': 0.0476,
    'city': 0.0476,
    'street_type': 0.0476,
    'unit_type': 0.0476,
}

potential_match_score_threshold = 60

# Confidence levels
confidence_levels = {
    'near-exact': 90,
    'high': 80,
    'medium': 70,
    'low': potential_match_score_threshold
}

def identify_matches(shopify_in, amazon_in,  no_name=False,
        threshold=potential_match_score_threshold, confidence_levels=confidence_levels
    ):
    '''
    Identify potential matches between Shopify and Amazon datasets based on address information.
    Parameters:
    shopify_in (pd.DataFrame): Input DataFrame containing Shopify data with columns 'shopify_id' and matchable columns.
    amazon_in (pd.DataFrame): Input DataFrame containing Amazon data with columns 'amazon_id' and matchable columns.
    threshold (float): The minimum match score required to consider a pair as a potential match. Default is potential_match_score_threshold.
    confidence_levels (dict): Dictionary defining the confidence levels based on match scores.
    Returns:
    list: A list of dictionaries, each containing:
        - 'shopify_id': The Shopify ID of the matched entry.
        - 'amazon_id': The Amazon ID of the matched entry.
        - 'score': The match score between the Shopify and Amazon entries.
        - 'confidence_level': The confidence level of the match ('near-exact', 'high', 'medium', 'low').
    '''
    if no_name:
        fields_to_remove = ['first_name', 'middle_name', 'middle_initial', 'last_name', 'full_name']
        filtered_columns = [col for col in matchable_columns if col not in fields_to_remove]
    else:
        filtered_columns = matchable_columns

    shop_cols = ['shopify_id'] + filtered_columns
    shopify = shopify_in[shop_cols]

    amazon_cols = ['amazon_id'] + filtered_columns
    amazon = amazon_in[amazon_cols]

    # First identify only zip_cleaned that are in both dfs
    zip_codes = set(shopify['zip_cleaned']).intersection(set(amazon['zip_cleaned']))
    
    print('There are an overlap of {} zip codes'.format(len(zip_codes)))

    matches = []

    for zip_code in tqdm(zip_codes):
        shopify_subset = shopify[shopify['zip_cleaned'] == zip_code]
        amazon_subset = amazon[amazon['zip_cleaned'] == zip_code]

        for _, shopify_row in shopify_subset.iterrows():
            for _, amazon_row in amazon_subset.iterrows():
                try:
                    if no_name:
                        score = calculate_match_score(shopify_row, amazon_row, no_name_weights)
                    else:
                        score = calculate_match_score(shopify_row, amazon_row, default_weights)
                    if score > threshold:
                        for level, min_score in confidence_levels.items():
                            if score >= min_score:
                                confidence_level = level
                                break
                        matches.append({
                            'shopify_id': shopify_row['shopify_id'],
                            'amazon_id': amazon_row['amazon_id'],
                            'score': score,
                            'confidence_level': confidence_level
                        })
                except Exception as e:
                    print(f"Error processing rows: {e}")
                    matches.append({
                        'shopify_id': shopify_row['shopify_id'],
                        'amazon_id': amazon_row['amazon_id'],
                        'score': None,
                        'confidence_level': None
                    })

    return pd.DataFrame(matches)


def calculate_match_score(shopify_row, amazon_row, weights=default_weights):
    """
    Calculate a weighted match score between Shopify and Amazon address records.
    Assumes zip_code has been pre-filtered and is not included in the scoring.

    Output is scaled to 0-100
    """

    # Extract fields from rows
    s_fields = {key: shopify_row.get(key, '') for key in weights.keys()}
    a_fields = {key: amazon_row.get(key, '') for key in weights.keys()}

    # Initialize total score
    total_score = 0

    # Comparison Logic

    # Exact match fields (No fuzzy matching needed)
    exact_match_fields = ['street_type', 'state', 'unit_type']

    for field in weights.keys():
        weight = weights[field]

        # Use exact match where applicable
        if field in exact_match_fields:
            score = 1.0 if s_fields[field] == a_fields[field] else 0.0
        
        # Use fuzzy match for fields with possible variations
        else:
            score = fuzz.ratio(s_fields[field], a_fields[field]) / 100

        # Apply weight
        total_score += weight * score

    # Penalty: If house numbers mismatch heavily, zero the score
    house_num_score = fuzz.ratio(s_fields['house_number'], a_fields['house_number']) / 100
    if house_num_score < 0.7:
        return 0

    return round(total_score * 100, 2)  # Scale to 0-100

def stitch_identified_data(shopify, amazon, matches, no_name=False):
    # Take the inputs of full shopify and amazon dfs and leverage the matching columns
    # Assuming matches, shopify, and amazon are already loaded DataFrames

    if no_name:
        fields_to_remove = ['first_name', 'middle_name', 'middle_initial', 'last_name', 'full_name']
        columns_to_drop = [col for col in matchable_columns if col not in fields_to_remove]
    else:
        columns_to_drop = matchable_columns

    # 1. Drop selected matchable columns and add suffixes
    shopify_filtered = shopify.drop(columns=columns_to_drop).add_suffix('_shopify')
    amazon_filtered = amazon.drop(columns=columns_to_drop).add_suffix('_amazon')

    # Rename the IDs back to their original names
    shopify_filtered = shopify_filtered.rename(columns={'shopify_id_shopify': 'shopify_id'})
    amazon_filtered = amazon_filtered.rename(columns={'amazon_id_amazon': 'amazon_id'})

    # 2. Add suffixes to matchable columns in Shopify and Amazon
    shopify_addy = shopify[matchable_columns].add_suffix('_addy_token')


    # 3. Merge matches with Shopify
    merged_df = matches.merge(shopify_filtered,on = 'shopify_id', how='left')

    # 4. Merge the result with Amazon, ensuring suffixes for all columns
    merged_df = merged_df.merge(amazon_filtered, on='amazon_id', how='left')

    # 5. Merge the address tokens back into the merged dataframe once
    merged_df = merged_df.merge(shopify_addy, left_on='shopify_id', right_index=True, how='left')

    # 6. Reorder columns to place 'score' at the beginning
    score_col = ['score']
    other_cols = [col for col in merged_df.columns if col != 'score']
    final_df = merged_df[score_col + other_cols]

    return final_df

def print_match_report(shopify, amazon, matches):
    # Number of unique IDs in the original dataframes
    unique_shopify_ids = shopify['shopify_id'].nunique()
    unique_amazon_ids = amazon['amazon_id'].nunique()

    # Number of unique IDs in the matches
    unique_matched_shopify_ids = matches['shopify_id'].nunique()
    unique_matched_amazon_ids = matches['amazon_id'].nunique()

    # Value counts of the confidence levels
    confidence_counts = matches['confidence_level'].value_counts()
    confidence_df = pd.DataFrame(confidence_counts).reset_index()
    confidence_df.columns = ['Confidence Level', 'Count']

    # Calculate matches as a percentage of the original dataframes
    shopify_match_percentage = (unique_matched_shopify_ids / unique_shopify_ids) * 100
    amazon_match_percentage = (unique_matched_amazon_ids / unique_amazon_ids) * 100

    # Print the report
    print("Match Report:")
    print(f"Total unique Shopify IDs: {unique_shopify_ids}")
    print(f"Total unique Amazon IDs: {unique_amazon_ids}")
    print(f"Unique matched Shopify IDs: {unique_matched_shopify_ids}")
    print(f"Unique matched Amazon IDs: {unique_matched_amazon_ids}")
    print(f"Shopify match percentage: {shopify_match_percentage:.2f}%")
    print(f"Amazon match percentage: {amazon_match_percentage:.2f}%")
    print("\nConfidence Level Counts:")
    print(confidence_df)
