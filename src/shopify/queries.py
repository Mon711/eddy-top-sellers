SHOP_INFO_QUERY = """
query {
  shop {
    name
    myshopifyDomain
    currencyCode
  }
}
"""

ORDERS_INSPECTION_QUERY = """
query OrdersInspection($orderQuery: String!, $first: Int!, $after: String) {
  orders(
    first: $first
    after: $after
    query: $orderQuery
    sortKey: CREATED_AT
    reverse: false
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }

    edges {
      cursor
      node {
        id
        name
        createdAt
        displayFinancialStatus
        tags

        currentTotalPriceSet {
          shopMoney {
            amount
            currencyCode
          }
        }

        lineItems(first: 50) {
          edges {
            node {
              id
              title
              quantity
              sku
              variantTitle

              originalTotalSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }

              discountedTotalSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }

              variant {
                id
                title
                sku

                product {
                  id
                  title
                  handle
                  productType
                  tags

                  featuredImage {
                    url
                    altText
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""
