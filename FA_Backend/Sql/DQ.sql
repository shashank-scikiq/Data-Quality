select * from od_dq_nhm odn;


-- ================================================================================
-- Table Creation script. 

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
select ord_date, seller_np ,(total_orders), (total_canceled_orders), (null_cans_code+null_cans_dt_time) as canc_metrices,(total_orders-total_canceled_orders) as completed_orders,
(null_fulfilment_id+null_net_tran_id+null_qty+null_itm_fulfilment_id+null_del_pc+null_created_date_time+null_domain+null_del_cty+
null_ord_stats+null_fulfil_status+null_itm_cat+null_cat_cons+null_sell_pincode+
null_prov_id+null_itm_id+null_sell_np+null_net_ord_id+null_sell_cty) as sum_missing_cols from aggregated_view av);





-- ================================================================================


-- Cancelled Order stats 
-- ========================================================== 
create view cancelled_ord_stats as (
select * from (
with null_counter as (
	select 
		dos.order_date,
		dos.seller_np,
		count(case when dos.cancellation_code is null or dos.cancellation_code = 'undefined' then 1 end) as null_count
		from dim_order_status dos 
		where dos.order_status = 'Cancelled'
		group by dos.order_date, dos.seller_np
), 
not_null_counter as (
	select 
		dos.order_date,
		dos.seller_np,
		count(case when dos.cancellation_code is not null or dos.cancellation_code != 'undefined' then 1 end) as not_null_count
		from dim_order_status dos 
		where dos.order_status = 'Cancelled'
		group by dos.order_date, dos.seller_np
), 
total_counter as (
	select dos.order_date, 
		dos.seller_np,
		count(dos.seller_np) as cancelled_orders
	from dim_order_status dos
	where dos.order_status = 'Cancelled'
	group by dos.order_date, dos.seller_np
) select tc.order_date, tc.seller_np, tc.cancelled_orders, nc.null_count, nnc.not_null_count
	from total_counter as tc
	left join not_null_counter as nnc
		on tc.order_date = nnc.order_date and tc.seller_np = nnc.seller_np
	left join null_counter nc 
		on tc.order_date = nc.order_date and tc.seller_np = nc.seller_np) as x
order by x.order_date, x.seller_np);


-- Order Status
-- =================================================================

create view completed_ord_status as (
select dos.order_date ,dos.order_status, dos.seller_np
from dim_order_status dos
where dos.order_status != 'Cancelled'
order by dos.order_status);


