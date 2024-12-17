-- Create Tables for Data Quality Report
-- =========================================================================================

-- OD_DQ_NHM
-- ==========================================================================================

select
	current_date as curr_date,
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) as ord_date,
	"seller np name" AS seller_np,
    SUM(CASE WHEN "Fulfillment Id" IS NULL THEN 1 ELSE 0 END) AS null_fulfilment_id,
    SUM(CASE WHEN "Network Transaction Id" IS NULL THEN 1 ELSE 0 END) AS null_net_tran_id,
    SUM(CASE WHEN "Qty" IS NULL THEN 1 ELSE 0 END) AS null_qty,
    SUM(CASE WHEN "Item Fulfillment Id" IS NULL THEN 1 ELSE 0 END) AS null_itm_fulfilment_id,
    SUM(CASE WHEN "Delivery Pincode" IS NULL OR 'Delivery Pincode' LIKE '%XXX%' THEN 1 ELSE 0 END) AS null_del_pc,
    SUM(CASE WHEN "O_Created Date & Time" IS NULL THEN 1 ELSE 0 END) AS null_created_date_time,
    SUM(CASE WHEN "Domain" IS NULL THEN 1 ELSE 0 END) AS null_domain,
    SUM(CASE WHEN "Delivery City" IS NULL OR "Delivery City" LIKE '%XXX%' THEN 1 ELSE 0 END) AS null_del_cty,
    SUM(CASE WHEN ("Order Status"='Cancelled') AND ("Cancellation Code" IS NULL  OR "Cancellation Code" LIKE '%Item Out of Stock%' OR "Cancellation Code" LIKE '%std:011%')THEN 1 ELSE 0 END) AS null_cans_code,
    SUM(CASE WHEN "Order Status"='Cancelled' AND "F_Cancelled At Date & Time" IS NULL THEN 1 ELSE 0 END) AS null_cans_dt_time,
    SUM(CASE WHEN "Order Status" IS NULL THEN 1 ELSE 0 END) AS null_ord_stats,
    SUM(CASE WHEN "Fulfillment Status" IS NULL THEN 1 ELSE 0 END) AS null_fulfil_status,
    SUM(CASE WHEN "Item Category" IS NULL THEN 1 ELSE 0 END) AS null_itm_cat,
    SUM(CASE WHEN "Item Consolidated Category" IS NULL THEN 1 ELSE 0 END) AS null_cat_cons,
    SUM(CASE WHEN "Seller Pincode" IS NULL OR "Seller Pincode" LIKE '%XXXX%' THEN 1 ELSE 0 END) AS null_sell_pincode,
    SUM(CASE WHEN "Provider id" IS NULL THEN 1 ELSE 0 END) AS null_prov_id,
    SUM(CASE WHEN "item id" IS NULL THEN 1 ELSE 0 END) AS null_itm_id,
    SUM(CASE WHEN "seller np name" IS NULL THEN 1 ELSE 0 END) AS null_sell_np,
    SUM(CASE WHEN "network order id" IS NULL THEN 1 ELSE 0 END) AS null_net_ord_id,
    SUM(CASE WHEN "seller city" IS NULL THEN 1 ELSE 0 END) AS null_sell_cty,
    count(*) as total_orders,
    SUM(CASE WHEN "Order Status" = 'Cancelled' THEN 1 ELSE 0 END) AS total_canceled_orders
FROM default.nhm_order_fulfillment_subset_v1
where
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) > date('2024-04-01')
GROUP by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name";

-- dim_sellers
-- ==========================================================================================

select
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) AS order_date,
	"seller np name" AS seller_np
from "default"."nhm_order_fulfillment_subset_v1"
where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) > Date('2024-04-01')
group by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name"
order by date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')), "seller np name";

-- dim_order_status
-- ==========================================================================================

select
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) order_date,
	"seller np name" AS seller_np,
	"Order Status" AS order_status,
	"Cancellation code" AS cancellation_code
from "default"."nhm_order_fulfillment_subset_v1"
where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) > Date('2024-04-01')
group by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name",
	"Order Status",
	"Cancellation code"
order by "seller np name";


-- Aggregated Tables.

-- agg_order_stats
-- ==========================================================================================

CREATE OR REPLACE VIEW data_sanity.agg_order_stats
AS SELECT order_date,
    order_status,
    seller_np,
    count(order_status) AS count
   FROM data_sanity.dim_order_status dos
  GROUP BY order_date, order_status, seller_np
  ORDER BY order_date DESC, seller_np;

-- aggregated_view
-- ==========================================================================================

CREATE MATERIALIZED VIEW data_sanity.aggregated_view
TABLESPACE pg_default
AS SELECT curr_date,
    ord_date,
    seller_np,
    sum(total_orders) AS total_orders,
    sum(total_canceled_orders) AS total_canceled_orders,
    sum(null_fulfilment_id) AS null_fulfilment_id,
    sum(null_net_tran_id) AS null_net_tran_id,
    sum(null_qty) AS null_qty,
    sum(null_itm_fulfilment_id) AS null_itm_fulfilment_id,
    sum(null_del_pc) AS null_del_pc,
    sum(null_created_date_time) AS null_created_date_time,
    sum(null_domain) AS null_domain,
    sum(null_del_cty) AS null_del_cty,
    sum(null_cans_code) AS null_cans_code,
    sum(null_cans_dt_time) AS null_cans_dt_time,
    sum(null_ord_stats) AS null_ord_stats,
    sum(null_fulfil_status) AS null_fulfil_status,
    sum(null_itm_cat) AS null_itm_cat,
    sum(null_cat_cons) AS null_cat_cons,
    sum(null_sell_pincode) AS null_sell_pincode,
    sum(null_prov_id) AS null_prov_id,
    sum(null_itm_id) AS null_itm_id,
    sum(null_sell_np) AS null_sell_np,
    sum(null_net_ord_id) AS null_net_ord_id,
    sum(null_sell_cty) AS null_sell_cty
   FROM data_sanity.od_dq_nhm odn
  GROUP BY curr_date, ord_date, seller_np
  ORDER BY curr_date DESC, ord_date DESC, seller_np
WITH DATA;

-- aggregated_sum
-- ==========================================================================================

CREATE OR REPLACE VIEW data_sanity.aggregated_sum
AS SELECT ord_date,
    seller_np,
    total_orders,
    total_canceled_orders,
    null_cans_code + null_cans_dt_time AS canc_metrices,
    total_orders - total_canceled_orders AS completed_orders,
    null_fulfilment_id + null_net_tran_id + null_qty + null_itm_fulfilment_id + null_del_pc + null_created_date_time + null_domain + null_del_cty + null_ord_stats + null_fulfil_status + null_itm_cat + null_cat_cons + null_sell_pincode + null_prov_id + null_itm_id + null_sell_np + null_net_ord_id + null_sell_cty AS sum_missing_cols
   FROM data_sanity.aggregated_view av;

-- col_sum
-- ==========================================================================================

CREATE OR REPLACE VIEW data_sanity.col_sum
AS SELECT ord_date,
    seller_np,
    sum(total_orders) AS total_orders,
    sum(total_canceled_orders) AS total_canceled_orders,
    sum(null_fulfilment_id) AS null_fulfilment_id,
    sum(null_net_tran_id) AS null_net_tran_id,
    sum(null_qty) AS null_qty,
    sum(null_itm_fulfilment_id) AS null_itm_fulfilment_id,
    sum(null_del_pc) AS null_del_pc,
    sum(null_cans_code) AS null_cans_code,
    sum(null_cans_dt_time) AS null_cans_dt_time,
    sum(null_ord_stats) AS null_ord_stats,
    sum(null_fulfil_status) AS null_fulfil_status,
    sum(null_itm_cat) AS null_itm_cat,
    sum(null_cat_cons) AS null_cat_cons,
    sum(null_sell_pincode) AS null_sell_pincode,
    sum(null_prov_id) AS null_prov_id,
    sum(null_itm_id) AS null_itm_id,
    sum(null_sell_np) AS null_sell_np,
    sum(null_net_ord_id) AS null_net_ord_id,
    sum(null_sell_cty) AS null_sell_cty,
    sum(null_del_cty) AS null_del_cty
   FROM data_sanity.aggregated_view
  GROUP BY ord_date, seller_np
  ORDER BY ord_date DESC, seller_np;


-- Create Tables for Data Sanity Report
-- =========================================================================================

--ds_last_run_date_query
-- =================================================================

create materialized view ds_last_run_date_query as (
WITH base_data AS (
                SELECT
                    month,
                    sub_domain_name as sub_domain,
                    dashboard,
                    distinct_order_count as doc,
                    distinct_order_count_till_last_run_date as doctlrd,
                    run_date, last_run_date
                FROM
                {DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL} where run_date = (select max(run_date) from {DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL})
            ),
            pivot_data AS (
                SELECT
                    month,
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS NO_OD_B2C,
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS NO_OD_B2B,
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS NO_OD_GV,
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS NO_OD_Logistics,
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS OD_L1_B2C,
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS OD_L1_B2B,
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS OD_L1_GV,
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS OD_L1_Logistics,
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS L1_L2_B2C,
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS L1_L2_B2B,
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS L1_L2_GV,
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS L1_L2_Logistics,
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS L2_L3_B2C,
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS L2_L3_B2B,
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS L2_L3_GV,
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS L2_L3_Logistics,
                    run_date
                FROM
                    base_data
                GROUP BY
                    month, run_date
            )
            SELECT
                month,
                NO_OD_B2C AS "NO-OD B2C",
                NO_OD_B2B AS "NO-OD B2B",
                NO_OD_GV AS "NO-OD GV",
                NO_OD_Logistics AS "NO-OD Logistics",
                OD_L1_B2C AS "OD-L1 B2C",
                OD_L1_B2B AS "OD-L1 B2B",
                OD_L1_GV AS "OD-L1 GV",
                OD_L1_Logistics AS "OD-L1 Logistics",
                L1_L2_B2C AS "L1-L2 B2C",
                L1_L2_B2B AS "L1-L2 B2B",
                L1_L2_GV AS "L1-L2 GV",
                L1_L2_Logistics AS "L1-L2 Logistics",
                L2_L3_B2C AS "L2-L3 B2C",
                L2_L3_B2B AS "L2-L3 B2B",
                L2_L3_GV AS "L2-L3 GV",
                L2_L3_Logistics AS "L2-L3 Logistics",
                run_date
            FROM
                pivot_data
            ORDER BY
                month DESC;