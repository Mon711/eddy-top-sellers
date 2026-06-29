import json

from shopify.client import run_shopify_query
from shopify.queries import ORDERS_INSPECTION_QUERY
from sales_records import build_sales_records


def load_json_config(file_path):
  """
    Reads a JSON config file and returns it as a Python dictionary.

    Example:
    config/seasons.json
    becomes usable Python data.
  """
  
  with open(file_path, "r") as file:
    return json.load(file)
  
  
def main():
    
    order_query = "created_at:>=2025-11-01 created_at:<=2026-05-31"
    
    variables = {
      "orderQuery": order_query,
      "first": 20
    }
    
    data = run_shopify_query(ORDERS_INSPECTION_QUERY, variables)
    
    seasons_config = load_json_config("config/seasons.json")
    accessory_config = load_json_config("config/accessory-exclusions.json")
    order_exclusions_config = load_json_config("config/order-exclusions.json")
    
    result = build_sales_records(
      shopify_data=data,
      seasons_config=seasons_config,
      accessory_config=accessory_config,
      order_exclusions_config=order_exclusions_config,
    )
    
    print(json.dumps(result, indent=2))
    
    
if __name__ == "__main__":
    main()
    
