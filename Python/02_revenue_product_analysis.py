
import pandas as pd
from pathlib import Path

# Load datasets
data_folder = Path(".")

orders = pd.read_csv(data_folder / "olist_orders_dataset.csv")
items = pd.read_csv(data_folder / "olist_order_items_dataset.csv")
products = pd.read_csv(data_folder / "olist_products_dataset.csv")
categories = pd.read_csv(
    data_folder / "product_category_name_translation.csv"
)

# Convert order purchase date
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

# Join order items with order dates and statuses
sales = items.merge(
    orders[
        ["order_id", "order_purchase_timestamp", "order_status"]
    ],
    on="order_id",
    how="left",
    validate="many_to_one"
)

# Join product information
sales = sales.merge(
    products[
        ["product_id", "product_category_name"]
    ],
    on="product_id",
    how="left",
    validate="many_to_one"
)

# Translate Portuguese category names into English
sales = sales.merge(
    categories,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)

# Calculate item revenue (excluding freight)
sales["item_revenue"] = sales["price"]

print("SALES DATA OVERVIEW")
print("Rows and columns:", sales.shape)
print("Unique orders:", sales["order_id"].nunique())
print("Unique products:", sales["product_id"].nunique())

print("\nTOTAL ITEM REVENUE BY ORDER STATUS")
print(
    sales.groupby("order_status")["item_revenue"]
    .sum()
    .round(2)
    .sort_values(ascending=False)
)

# Revenue by month
sales["purchase_month"] = (
    sales["order_purchase_timestamp"].dt.to_period("M").astype(str)
)

monthly_revenue = (
    sales.groupby("purchase_month")["item_revenue"]
    .sum()
    .reset_index()
    .sort_values("purchase_month")
)

print("\nTOP 5 MONTHS BY ITEM REVENUE")
print(
    monthly_revenue.sort_values(
        "item_revenue", ascending=False
    ).head(5).to_string(index=False)
)

# Top product categories
category_column = "product_category_name_english"

sales["category"] = sales[category_column].fillna(
    sales["product_category_name"].fillna("Unknown")
)

top_categories = (
    sales.groupby("category")
    .agg(
        item_revenue=("item_revenue", "sum"),
        items_sold=("order_item_id", "count")
    )
    .sort_values("item_revenue", ascending=False)
    .head(10)
)

print("\nTOP 10 PRODUCT CATEGORIES BY ITEM REVENUE")
print(top_categories.round(2).to_string())

# Save analysis results
monthly_revenue.to_csv("monthly_revenue_summary.csv", index=False)
top_categories.to_csv("top_product_categories.csv")

print("\nSaved monthly_revenue_summary.csv")
print("Saved top_product_categories.csv")
