import requests

from config import (
    SHOPIFY_STORE_DOMAIN,
    SHOPIFY_ADMIN_ACCESS_TOKEN,
    SHOPIFY_API_VERSION,
)

def run_shopify_query(query, variables=None):
    url = f"https://{SHOPIFY_STORE_DOMAIN}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_ADMIN_ACCESS_TOKEN,
    }
    
    payload = {
        "query": query,
        "variables": variables or {},
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    result = response.json()
    
    if "errors" in result:
        raise Exception(result["errors"])
    
    return result["data"]