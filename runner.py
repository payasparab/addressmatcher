# File to run all of the functions needed from command line

from data_science.data_loaders import load_shopify_data, load_amazon_data, load_netsuite_data
from data_science.match_algo import identify_matches, stitch_identified_data, print_match_report
import sys

# First need to clean up messy file
# TODO 
# Need to load the new messy file and apply amazon cleaner
#TODO

# Need to load the shopify file if it hasn't been cleaned recently AKA TEMP file available
def generate_matches(amazon_path, shopify_path=None, use_cache=False):
    shopify = load_shopify_data(path=shopify_path, use_cache=use_cache)
    amazon = load_amazon_data(path=amazon_path)
    matches = identify_matches(shopify, amazon)
    final_df = stitch_identified_data(shopify, amazon, matches)
    print_match_report(shopify, amazon, matches)
    return final_df

def generate_matches_netsuite(netsuite_path, shopify_path=None, use_cache=False):
    shopify = load_shopify_data(path=shopify_path, use_cache=use_cache)
    netsuite = load_netsuite_data(path=netsuite_path)
    matches = identify_matches(shopify, netsuite, no_name=True)
    final_df = stitch_identified_data(shopify, netsuite, matches)
    print_match_report(shopify, netsuite, matches)
    return final_df

def main():
    if len(sys.argv) < 2:
        print("Usage: python runner.py <amazon_path> [shopify_path] [--use_cache]")
        sys.exit(1)
    
    amazon_path = sys.argv[1]
    shopify_path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    use_cache = "--use_cache" in sys.argv
    
    generate_matches(amazon_path, shopify_path, use_cache)

if __name__ == "__main__":
    main()
# Need to run match algo

# Need to save the results