# Development Notes

## Pagination Validation

Tested pagination implementation with 5 orders:
- **Test 1**: Retrieved all orders at once
- **Test 2**: Retrieved orders with pagination (2 at a time)
- **Result**: Both datasets match exactly with no duplicate line items

## Data Validation via ShopifyQL

### ShopifyQL Query Template

Used the following query to cross-check data for top sellers by product and month. Note that color and size are combined in the `product_variant_title` field, requiring manual aggregation for color-level reporting.

```ShopifyQL
FROM sales
  SHOW net_sales, gross_sales, net_items_sold
  WHERE product_title = 'ASD X AGV House Dress'
    AND line_type = 'product'
    AND is_sales_reversal = false
    AND order_payment_status NOT IN ('refunded', 'voided')
    AND order_tags NOT CONTAINS 'gift card'
    AND order_tags NOT CONTAINS 'refund'
    AND order_tags NOT CONTAINS 'zero refund'
    AND order_tags NOT CONTAINS 'exchange'
  GROUP BY product_variant_title WITH TOTALS
  HAVING net_sales > 0
  SINCE 2025-11-01 UNTIL 2025-11-30
  ORDER BY net_sales ASC
```

**Usage**: Replace `ASD X AGV House Dress` with the product title and update the date range (`SINCE`/`UNTIL`) as needed.

### Key Limitations
- ShopifyQL cannot separate color and size; they appear together in `product_variant_title`
- Color-level aggregation must be calculated manually

## Access & Credentials

Shopify account accessible via Google account sign-in. Credentials stored in Apple Passwords (Creatnet folder).