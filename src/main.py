import json

from shopify.client import run_shopify_query
from shopify.queries import ORDERS_INSPECTION_QUERY
from sales_records import build_sales_records
from aggregations import build_overall_rows


def load_json_config(file_path):
    """
    Reads a JSON config file and returns it as a Python dictionary.

    Example:
    config/seasons.json
    becomes usable Python data.
    """

    with open(file_path, "r") as file:
        return json.load(file)


def fetch_all_orders(order_query):
    """
    Fetches all Shopify orders for the given order query.

    Shopify GraphQL returns orders in pages.
    This function keeps fetching pages until Shopify says there are no more.
    """

    all_order_edges = []
    after = None

    while True:
        variables = {
            "orderQuery": order_query,
            "first": 100,
            "after": after,
        }

        data = run_shopify_query(ORDERS_INSPECTION_QUERY, variables)

        orders = data.get("orders", {})
        edges = orders.get("edges", [])
        page_info = orders.get("pageInfo", {})

        all_order_edges.extend(edges)

        print(f"Fetched {len(all_order_edges)} orders so far...")

        if not page_info.get("hasNextPage"):
            break

        after = page_info.get("endCursor")

    return {"orders": {"edges": all_order_edges}}


def main():

    order_query = "created_at:>=2025-11-01 created_at:<=2026-05-31"

    data = fetch_all_orders(order_query)

    seasons_config = load_json_config("config/seasons.json")
    accessory_config = load_json_config("config/accessory-exclusions.json")
    order_exclusions_config = load_json_config("config/order-exclusions.json")

    result = build_sales_records(
        shopify_data=data,
        seasons_config=seasons_config,
        accessory_config=accessory_config,
        order_exclusions_config=order_exclusions_config,
    )

    overall_rows = build_overall_rows(result["cleaned_records"])

    with open("data/output.json", "w") as file:
        json.dump(data, file, indent=2)

    with open("data/cleaned_output", "w") as file:
        json.dump(result, file, indent=2)

    with open("data/aggregated_output.json", "w") as file:
        json.dump(overall_rows, file, indent=2)

    print("Done.")
    print(f"Cleaned records: {len(result['cleaned_records'])}")
    print(f"Skipped records: {len(result['skipped_records'])}")
    print(f"Overall rows: {len(overall_rows)}")


if __name__ == "__main__":
    main()
