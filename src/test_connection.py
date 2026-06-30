from shopify.client import run_shopify_query
from shopify.queries import SHOP_INFO_QUERY


def test():
    data = run_shopify_query(SHOP_INFO_QUERY)

    shop = data["shop"]

    print("Connected to Shopify")
    print(f"Store: {shop['name']}")
    print(f"Domain: {shop['myshopifyDomain']}")
    print(f"Currency: {shop['currencyCode']}")
