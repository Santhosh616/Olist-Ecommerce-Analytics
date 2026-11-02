
import pandas as pd
from pathlib import Path

# Load the orders dataset
data_folder = Path(".")
orders = pd.read_csv(data_folder / "olist_orders_dataset.csv")

# 1. Dataset overview
print("DATASET OVERVIEW")
print("Rows and columns:", orders.shape)
print("Duplicate rows:", orders.duplicated().sum())
print("Unique order IDs:", orders["order_id"].nunique())

# 2. Order status analysis
print("\nORDER STATUS COUNTS")
print(orders["order_status"].value_counts())

print("\nORDER STATUS PERCENTAGES")
print(
    (orders["order_status"].value_counts(normalize=True) * 100)
    .round(2)
)

# 3. Convert purchase timestamp to datetime
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"],
    errors="coerce"
)

print("\nPURCHASE DATE RANGE")
print("Earliest:", orders["order_purchase_timestamp"].min())
print("Latest:", orders["order_purchase_timestamp"].max())

# 4. Purchases by year
orders["purchase_year"] = (
    orders["order_purchase_timestamp"].dt.year
)

print("\nORDERS BY YEAR")
print(orders["purchase_year"].value_counts().sort_index())

# 5. Missing values
print("\nMISSING VALUES")
print(orders.isnull().sum())


# 6. Monthly order trend

orders["purchase_month"] = (
    orders["order_purchase_timestamp"].dt.to_period("M")
)

monthly_orders = (
    orders.groupby("purchase_month")["order_id"]
    .nunique()
    .reset_index(name="total_orders")
)

monthly_orders["purchase_month"] = (
    monthly_orders["purchase_month"].astype(str)
)

print("\nMONTHLY ORDER TREND")
print(monthly_orders.to_string(index=False))

print("\nTOP 5 MONTHS BY NUMBER OF ORDERS")
print(
    monthly_orders.sort_values(
        "total_orders", ascending=False
    ).head(5).to_string(index=False)
)

# Save the monthly summary for later use
monthly_orders.to_csv("monthly_orders_summary.csv", index=False)

print("\nMonthly summary saved successfully.")

