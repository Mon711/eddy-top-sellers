def build_overall_rows(cleaned_records):
    """
    Builds rows for the Overall sheet.

    Groups sales by:

    month_key
    season_code
    product_title
    color

    This combines different sizes and SKUs into one row.
    """
    grouped_records = {}

    for record in cleaned_records:
        group_key = (
            record.get("month_key"),
            record.get("season_code"),
            record.get("product_title"),
            record.get("color"),
        )

        if group_key not in grouped_records:
            grouped_records[group_key] = {
                "month_key": record.get("month_key"),
                "month_label": record.get("month_label"),
                "season_code": record.get("season_code"),
                "season_name": record.get("season_name"),
                "product_title": record.get("product_title"),
                "color": record.get("color"),
                "net_items": 0,
                "net_sales": 0.0,
                "sample_sku": record.get("sku"),
                "product_url": record.get("product_url"),
                "image_url": record.get("image_url"),
            }

        grouped_records[group_key]["net_items"] += record.get("quantity", 0)
        grouped_records[group_key]["net_sales"] += record.get("net_sales", 0)

    sorted_groups = sorted(
        grouped_records.values(),
        key=lambda row: (
            -row["net_sales"],
            -row["net_items"],
            row["product_title"] or "",
            row["color"] or "",
        ),
    )

    overall_rows = []

    for index, row in enumerate(sorted_groups, start=1):
        overall_rows.append(
            {
                "#": index,
                "Product Title": row["product_title"],
                "Month": row["month_label"],
                "Season": row["season_name"],
                "Color": row["color"],
                "Net Items": row["net_items"],
                "Net Sales": round(row["net_sales"], 2),
                "SKU": row["sample_sku"],
                "Product Page & Images": row["product_url"],
            }
        )

    return overall_rows
