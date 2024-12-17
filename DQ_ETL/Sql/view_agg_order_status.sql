CREATE OR REPLACE VIEW "PG_SCHEMA"."AGG_ORD_STATS"
AS SELECT order_date,
    order_status,
    seller_np,
    count(order_status) AS count
   FROM "PG_SCHEMA"."DIM_ORD_STAT" dos
  GROUP BY order_date, order_status, seller_np
  ORDER BY order_date DESC, seller_np;
