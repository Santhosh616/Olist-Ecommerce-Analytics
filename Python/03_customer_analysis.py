
import pandas as pd
from pathlib import Path

data_folder = Path(".")

# Load datasets
orders = pd.read_csv(data_folder / "olist_orders_dataset.csv")
customers = pd.read_csv(data_folder / "olist_customers_dataset.csv")
payments = pd.read_csv(data_folder / "olist_order_payments_dataset.csv")
items = pd.read_csv(data_folder / "olist_order_items_dataset.csv")

# Convert purchase timestamp
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

# 1. Customer overview
customer_orders = orders.merge(
    customers[["customer_id", "customer_unique_id",
               "customer_state"]],
    on="customer_id",
    how="left",
    validate="many_to_one"
)

print("CUSTOMER OVERVIEW")
print("Order records:", len(orders))
print("Unique customer IDs:", customer_orders["customer_id"].nunique())
print("Unique individual customers:",
      customer_orders["customer_unique_id"].nunique())

# 2. Repeat purchase analysis
orders_per_customer = (
    customer_orders.groupby("customer_unique_id")["order_id"]
    .nunique()
)

repeat_customers = (orders_per_customer > 1).sum()
total_customers = orders_per_customer.nunique()

print("\nREPEAT PURCHASE ANALYSIS")
print("Customers with multiple orders:", repeat_customers)
print("Customers with one order:",
      (orders_per_customer == 1).sum())
print("Repeat customer percentage:",
      round(repeat_customers / len(orders_per_customer) * 100, 2), "%")

# 3. Customers by state
state_customers = (
    customer_orders.groupby("customer_state")["customer_unique_id"]
    .nunique()
    .sort_values(ascending=False)
)

print("\nTOP 10 STATES BY UNIQUE CUSTOMERS")
print(state_customers.head(10))

# 4. Payment method analysis
print("\nPAYMENT METHOD ANALYSIS")
print(
    payments.groupby("payment_type")
    .agg(
        payment_records=("order_id", "size"),
        total_payment_value=("payment_value", "sum")
    )
    .sort_values("total_payment_value", ascending=False)
    .round(2)
)

# 5. Item revenue from delivered orders only
delivered_orders = orders.loc[
    orders["order_status"] == "delivered", ["order_id"]
]

delivered_items = items.merge(
    delivered_orders,
    on="order_id",
    how="inner",
    validate="many_to_one"
)

print("\nDELIVERED-ORDER ITEM REVENUE")
print("Delivered orders with item records:",
      delivered_items["order_id"].nunique())
print("Delivered-order item revenue (R$):",
      round(delivered_items["price"].sum(), 2))

# 6. Save results
state_customers.rename("unique_customers").to_csv(
    "customers_by_state.csv"
)

print("\nSaved customers_by_state.csv")
