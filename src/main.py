from shopify_client import run_shopify_query

def main():
    query = """
    query {
      shop {
        name
        myshopifyDomain
        currencyCode
      }
    }
    """
    
    data = run_shopify_query(query)
    
    shop = data["shop"]
    
    print("Connected to Shopify")
    print(f"Store: {shop['name']}")
    print(f"Domain: {shop['myshopifyDomain']}")
    print(f"Currency: {shop['currencyCode']}")
    
    
if __name__ == "__main__":
    main()
    
