-- Table Creation script. 

-- aggregated_view 
-- ================================================================================

create materialized view aggregated_view as(
select curr_date, ord_date,seller_np, 
	sum(total_orders) as total_orders,
	sum(total_canceled_orders) as total_canceled_orders,
	sum(null_fulfilment_id) as null_fulfilment_id,
	sum(null_net_tran_id) as null_net_tran_id,
	sum(null_qty) as null_qty,
	sum(null_itm_fulfilment_id) as null_itm_fulfilment_id,
	sum(null_del_pc) as null_del_pc, 
	sum(null_created_date_time) as null_created_date_time, 
	sum(null_domain) as null_domain,
	sum(null_del_cty) as null_del_cty,
	sum(null_cans_code) as null_cans_code,
	sum(null_cans_dt_time) as null_cans_dt_time, 
	sum(null_ord_stats) as null_ord_stats, sum(null_fulfil_status) as null_fulfil_status, 
	sum(null_itm_cat) as null_itm_cat, sum(null_cat_cons) as null_cat_cons, 
	sum(null_sell_pincode) as null_sell_pincode, sum(null_prov_id) as null_prov_id, 
	sum(null_itm_id) as null_itm_id, sum(null_sell_np) as null_sell_np, 
	sum(null_net_ord_id) as null_net_ord_id, sum(null_sell_cty) as null_sell_cty
from od_dq_nhm odn
group by curr_date, ord_date, seller_np
order by curr_date desc, ord_date desc, seller_np);

REFRESH MATERIALIZED VIEW agg_order_stats;
REFRESH MATERIALIZED VIEW aggregated_view;


-- col_sum 
-- ================================================================================

create view col_sum as (
select ord_date, 
	seller_np,
	sum(total_orders) as total_orders, 
	sum(total_canceled_orders) as total_canceled_orders,
	sum(null_fulfilment_id) as null_fulfilment_id,
	sum(null_net_tran_id) as null_net_tran_id,
	sum(null_qty) as null_qty,
	sum(null_itm_fulfilment_id) as null_itm_fulfilment_id,
	sum(null_del_pc) as null_del_pc,
	sum(null_cans_code) as null_cans_code,
	sum(null_cans_dt_time) as null_cans_dt_time,
	sum(null_ord_stats) as null_ord_stats,
	sum(null_fulfil_status) as null_fulfil_status,
	sum(null_itm_cat) as null_itm_cat,
	sum(null_cat_cons) as null_cat_cons,
	sum(null_sell_pincode) as null_sell_pincode,
	sum(null_prov_id) as null_prov_id,
	sum(null_itm_id) as null_itm_id,
	sum(null_sell_np) as null_sell_np,
	sum(null_net_ord_id) as null_net_ord_id,
	sum(null_sell_cty) as null_sell_cty
from aggregated_view
group by ord_date, seller_np
order by ord_date desc, seller_np);


-- aggregated_sum
-- ================================================================================
create view aggregated_sum as (
select ord_date, seller_np ,(total_orders), (total_canceled_orders), 
	(null_cans_code+null_cans_dt_time) as canc_metrices,
	(total_orders-total_canceled_orders) as completed_orders,
	(null_fulfilment_id+null_net_tran_id+null_qty+null_itm_fulfilment_id+null_del_pc+
	null_created_date_time+null_domain+null_del_cty+
	null_ord_stats+null_fulfil_status+null_itm_cat+null_cat_cons+null_sell_pincode+
	null_prov_id+null_itm_id+null_sell_np+null_net_ord_id+null_sell_cty) as sum_missing_cols 
from aggregated_view av);


-- agg_order_stats
-- ========================================================== 
create view agg_order_stats as (
select dos.order_date, dos.order_status,dos.seller_np, count(dos.order_status) from dim_order_status dos 
group by dos.order_date, dos.order_status, dos.seller_np
order by dos.order_date desc, dos.seller_np);
