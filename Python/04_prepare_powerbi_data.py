
import pandas as pd
from pathlib import Path

data_folder = Path(".")
output_folder = Path("powerbi_data")
output_folder.mkdir(exist_ok=True)

# Load datasets
orders = pd.read_csv(data_folder / "olist_orders_dataset.csv")
items = pd.read_csv(data_folder / "olist_order_items_dataset.csv")
products = pd.read_csv(data_folder / "olist_products_dataset.csv")
customers = pd.read_csv(data_folder / "olist_customers_dataset.csv")
payments = pd.read_csv(data_folder / "olist_order_payments_dataset.csv")
categories = pd.read_csv(
    data_folder / "product_category_name_translation.csv"
)

# Convert purchase date
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

# 1. Order status summary
order_status = (
    orders.groupby("order_status")
    .agg(total_orders=("order_id", "nunique"))
    .reset_index()
)
order_status.to_csv(output_folder / "order_status_summary.csv", index=False)

# 2. Monthly orders
orders["purchase_month"] = (
    orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
)
monthly_orders = (
    orders.groupby("purchase_month")
    .agg(total_orders=("order_id", "nunique"))
    .reset_index()
)
monthly_orders.to_csv(output_folder / "monthly_orders.csv", index=False)

# 3. Monthly delivered-order item revenue
delivered_ids = orders.loc[
    orders["order_status"] == "delivered", ["order_id", "purchase_month"]
]

delivered_sales = items.merge(
    delivered_ids,
    on="order_id",
    how="inner",
    validate="many_to_one"
)

monthly_revenue = (
    delivered_sales.groupby("purchase_month")
    .agg(item_revenue=("price", "sum"))
    .reset_index()
)
monthly_revenue.to_csv(
    output_folder / "monthly_delivered_item_revenue.csv", index=False
)

# 4. Revenue by product category
category_sales = items.merge(
    products[["product_id", "product_category_name"]],
    on="product_id",
    how="left",
    validate="many_to_one"
)

category_sales = category_sales.merge(
    categories,
    on="product_category_name",
    how="left",
    validate="many_to_one"
)

category_sales["category"] = (
    category_sales["product_category_name_english"]
    .fillna(category_sales["product_category_name"])
    .fillna("Unknown")
)

category_summary = (
    category_sales.groupby("category")
    .agg(
        item_revenue=("price", "sum"),
        items_sold=("order_item_id", "count")
    )
    .reset_index()
    .sort_values("item_revenue", ascending=False)
)

category_summary.to_csv(
    output_folder / "category_performance.csv", index=False
)

# 5. Unique customers by state
customer_summary = (
    customers.groupby("customer_state")
    .agg(unique_customers=("customer_unique_id", "nunique"))
    .reset_index()
    .sort_values("unique_customers", ascending=False)
)

customer_summary.to_csv(
    output_folder / "customers_by_state.csv", index=False
)

# 6. Payment methods
payment_summary = (
    payments.groupby("payment_type")
    .agg(
        payment_records=("order_id", "size"),
        total_payment_value=("payment_value", "sum")
    )
    .reset_index()
)

payment_summary.to_csv(
    output_folder / "payment_methods.csv", index=False
)

print("Power BI data preparation complete.")
print("Files saved in:", output_folder.resolve())
print("Summary files created:", len(list(output_folder.glob("*.csv"))))
