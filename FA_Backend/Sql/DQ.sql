-- Top N Sellers with Previous date stats 

select curr_date , seller_np, sum(null_del_cty) as total_del_city, sum(total_orders) as total_orders from od_dq_nhm odn 
where curr_date in ('2024-06-26', '2024-06-25')
--seller_np in ('shikhar-ondc.hulcd.com', 'retailconnect.co.in', 'biz.ondc.mcdindia.com', 
--'prod-wellify-bpp.shopalyst.com', 'sellerappapi.ninjacart.in')
group by seller_np,curr_date
order by seller_np, curr_date asc;


-- Total Orders with Delta
select ord_date, sum(total_orders) as sum_ttl, sum(total_canceled_orders) as sum_canc
from od_dq_nhm odn 
where ord_date in ('2024-06-24', '2024-06-25')
group by ord_date;

select * from od_dq_nhm odn;

-- Aggregated View 
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

select * from aggregated_view;

--REFRESH MATERIALIZED VIEW aggregated_view;


select * from aggregated_view av where av.ord_date = '2024-06-25';

select ord_date, 
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
group by ord_date
order by ord_date desc;



create view aggregated_sum as (
select ord_date, seller_np ,(total_orders), (total_canceled_orders), (null_cans_code+null_cans_dt_time) as canc_metrices,(total_orders-total_canceled_orders) as missing_total_base,
(null_fulfilment_id+null_net_tran_id+null_qty+null_itm_fulfilment_id+null_del_pc+null_created_date_time+null_domain+null_del_cty+
null_ord_stats+null_fulfil_status+null_itm_cat+null_cat_cons+null_sell_pincode+
null_prov_id+null_itm_id+null_sell_np+null_net_ord_id+null_sell_cty) as missing_from_total from aggregated_view av);


select * from aggregated_sum;

select * from aggregated_sum where seller_np = 'agg.dominos.co.in';


select ord_date, sum(total_orders) as total_orders,
sum(total_canceled_orders) as total_canceled_orders from aggregated_sum
group by ord_date
order by ord_date desc;

select seller_np, sum(total_orders) as total_orders, sum(total_canceled_orders) as total_canceled_orders,
	sum(canc_metrices) as canc_metrices, sum(missing_total_base) as missing_total_base, sum(missing_from_total) as missing_from_total
from aggregated_sum
group by seller_np
order by missing_total_base desc;



select
	sum(total_orders) as total_orders, 
	sum(null_fulfilment_id) as null_fulfilment_id,
	sum(null_net_tran_id) as null_net_tran_id,
	sum(null_qty) as null_qty,
	sum(null_itm_fulfilment_id) as null_itm_fulfilment_id,
	sum(null_del_pc) as null_del_pc,
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
from aggregated_view;
