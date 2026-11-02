USE olist_analytics;

-- 1. Total number of orders
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM orders;

-- 2. Order status distribution
SELECT
    order_status,
    COUNT(*) AS total_orders
FROM orders
GROUP BY order_status
ORDER BY total_orders DESC;

-- 3. Total sales
SELECT
    ROUND(SUM(price), 2) AS total_item_sales
FROM order_items;

-- 4. Top 10 product categories by sales
SELECT
    p.product_category_name,
    ROUND(SUM(oi.price), 2) AS total_sales
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC
LIMIT 10;