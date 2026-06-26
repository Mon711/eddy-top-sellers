import json

from shopify.client import run_shopify_query
from shopify.queries import ORDERS_INSPECTION_QUERY

def main():
    
    order_query = "created_at:>=2025-11-01 created_at:<=2026-05-31"
    
    variables = {
      "orderQuery": order_query,
      "first": 20
    }
    
    data = run_shopify_query(ORDERS_INSPECTION_QUERY, variables)
    
    print(json.dumps(data, indent=2))
    
    
if __name__ == "__main__":
    main()
    
