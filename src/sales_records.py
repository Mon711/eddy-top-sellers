from datetime import datetime


def parse_variant_title(variant_title):
    """
    Splits Shopify variant titles like:
    'Small / Raspberry'

    into:
    size = 'Small'
    color = 'Raspberry'
    """

    if not variant_title:
        return {"size": None, "color": None}

    parts = variant_title.split(" / ")

    if len(parts) == 1:
        return {"size": None, "color": parts[0].strip()}

    size = parts[0].strip()
    color = " / ".join(parts[1:]).strip()

    return {
        "size": size,
        "color": color,
    }


def get_month_key_and_label(created_at):
    """
    Converts Shopify order date into:

    month_key:   '2025-11'
    month_label: 'November 2025'

    month_key is for grouping and sorting.
    month_label is what we show in the final report.
    """

    order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

    return {
        "order_date": order_date.date().isoformat(),
        "month_key": order_date.strftime("%Y-%m"),
        "month_label": order_date.strftime("%B %Y"),
    }


def get_product_season(product_tags, seasons_config):
    """
    Finds the product season from Shopify product tags.

    Example:
    product tags contain 'HOL25'
    seasons_config contains:
    {
        'HOL25': 'Holiday 2025'
    }

    Then this returns:
    {
        'season_code': 'HOL25',
        'season_name': 'Holiday 2025'
    }
    """

    if not product_tags:
        return None

    normalized_tags = {tags.strip().lower() for tags in product_tags}

    for season_code, season_name in seasons_config.items():
        normalized_season_code = season_code.strip().lower()

        if normalized_season_code in normalized_tags:
            return {
                "season_code": season_code,
                "season_name": season_name,
            }
    return None


def money_amount(money_set):
    """
    Safely extracts a numeric amount from Shopify money fields.

    Shopify gives us:
    {
        'shopMoney': {
            'amount': '278.6',
            'currencyCode': 'USD'
        }
    }

    This returns:
    278.6
    """

    if not money_set:
        return 0.0

    shop_money = money_set.get("shopMoney", {})
    amount = shop_money.get("amount", 0)

    return float(amount)


def should_skip_order(order, order_exclusions_config):
    """
    Decides whether the whole order should be ignored.

    The rules come from:
    config/order-exclusions.json
    """
    excluded_statuses = order_exclusions_config.get("financialStatuses", [])
    excluded_tag_keywords = order_exclusions_config.get("orderTagKeywords", [])
    excluded_zero_dollar_orders = order_exclusions_config.get(
        "excludeZeroDollarOrders",
        True,
    )

    financial_status = order.get("displayFinancialStatus")

    if financial_status in excluded_statuses:
        return {"skip": True, "reason": f"excluded_financial_status:{financial_status}"}

    order_total = money_amount(order.get("currentTotalPriceSet"))

    if excluded_zero_dollar_orders and order_total <= 0:
        return {
            "skip": True,
            "reason": "zero_order_total",
        }

    order_tags = order.get("tags", [])

    normalized_order_tags = [tag.strip().lower() for tag in order_tags]

    for tag in normalized_order_tags:
        for keyword in excluded_tag_keywords:
            if keyword.lower() in tag:
                return {
                    "skip": True,
                    "reason": f"excluded_order_tag:{tag}",
                }

    return {
        "skip": False,
        "reason": None,
    }


def is_accessory_product(product, accessory_config):
    """
    Decides whether a product is an accessory.

    The rules come from:
    config/accessory-exclusions.json
    """

    product_title = product.get("title", "") or ""
    product_type = product.get("productType", "") or ""
    product_tags = product.get("tags", []) or []

    product_title_lower = product_title.lower()
    product_type_lower = product_type.lower()
    product_tags_lower = [tag.lower() for tag in product_tags]

    title_keywords = accessory_config.get("productTitleKeywords", [])
    type_keywords = accessory_config.get("productTypeKeywords", [])
    tag_keywords = accessory_config.get("tagKeywords", [])

    for keyword in title_keywords:
        if keyword.lower() in product_title_lower:
            return True

    for keyword in type_keywords:
        if keyword.lower() in product_type_lower:
            return True

    for keyword in tag_keywords:
        keyword_lower = keyword.lower()

        for tag in product_tags_lower:
            if keyword_lower in tag:
                return True

    return False


# !NOTE: The urls are showing 404 not found, so have to change this fn.
def build_product_url(product_handle):
    """
    Builds the public ShopEddy product URL from the Shopify product handle.
    """

    if not product_handle:
        return None

    return f"https://shopeddy.com/products/{product_handle}"


def build_sales_records(
    shopify_data,
    seasons_config,
    accessory_config,
    order_exclusions_config,
):
    """
    Main function.

    Takes raw Shopify GraphQL order data.
    Returns clean line-item sales records.

    One cleaned record = one valid Shopify line item.
    Later, will aggregate these records into the 3 report sheets.
    """

    cleaned_records = []
    skipped_records = []

    orders = shopify_data.get("orders", {}).get("edges", [])

    for order_edge in orders:
        order = order_edge.get("node", {})

        order_skip_result = should_skip_order(
            order=order,
            order_exclusions_config=order_exclusions_config,
        )

        line_items = order.get("lineItems", {}).get("edges", [])

        for line_item_edge in line_items:
            line_item = line_item_edge.get("node", {})

            variant = line_item.get("variant") or {}
            product = variant.get("product") or {}

            if order_skip_result["skip"]:
                skipped_records.append(
                    {
                        "order_name": order.get("name"),
                        "product_title": line_item.get("title"),
                        "skip_reason": order_skip_result["reason"],
                    }
                )
                continue

            if is_accessory_product(product, accessory_config):
                skipped_records.append(
                    {
                        "order_name": order.get("name"),
                        "product_title": line_item.get("title"),
                        "skip_reason": "accessory_product",
                    }
                )
                continue

            season = get_product_season(
                product_tags=product.get("tags", []),
                seasons_config=seasons_config,
            )

            if not season:
                skipped_records.append(
                    {
                        "order_name": order.get("name"),
                        "product_title": line_item.get("title"),
                        "skip_reason": "season_not_in_report",
                    }
                )
                continue

            variant_parts = parse_variant_title(line_item.get("variantTitle"))

            date_parts = get_month_key_and_label(order.get("createdAt"))

            product_handle = product.get("handle")
            featured_image = product.get("featuredImage") or {}

            cleaned_record = {
                "order_id": order.get("id"),
                "order_name": order.get("name"),
                "order_date": date_parts["order_date"],
                "month_key": date_parts["month_key"],
                "month_label": date_parts["month_label"],
                "product_id": product.get("id"),
                "product_title": product.get("title") or line_item.get("title"),
                "product_handle": product_handle,
                "product_url": build_product_url(product_handle),
                "image_url": featured_image.get("url"),
                "variant_id": variant.get("id"),
                "variant_title": line_item.get("variantTitle"),
                "size": variant_parts["size"],
                "color": variant_parts["color"],
                "sku": line_item.get("sku") or variant.get("sku"),
                "season_code": season["season_code"],
                "season_name": season["season_name"],
                "quantity": line_item.get("quantity", 0),
                "net_sales": money_amount(line_item.get("discountedTotalSet")),
            }

            cleaned_records.append(cleaned_record)

    return {
        "cleaned_records": cleaned_records,
        "skipped_records": skipped_records,
    }
