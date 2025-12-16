### Testing all of the key data cleaning functions
def test_data_cleaning():
    from data_science.data_loaders import load_shopify_data, load_amazon_data
    shopify = load_shopify_data(test=True)
    amazon = load_amazon_data(test=True)
    return shopify, amazon

def test_match_algo():
    from data_science.match_algo import identify_matches, stitch_identified_data, print_match_report
    shopify, amazon = test_data_cleaning()
    matches = identify_matches(shopify, amazon)
    final_df = stitch_identified_data(shopify, amazon, matches)
    print_match_report(shopify, amazon, matches)
    return final_df