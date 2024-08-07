select max(order_date) from staging_all.category_level_orders;  
-- (2024-04-04)


-- Analyse SWCLO vs Agg on provider_key
-- ====================================================================

select count(distinct provider_key)
from staging_all.category_level_orders
where order_date = '2024-04-04';

select count(distinct provider_key)
from staging_all.fact_order_detail fod 
where order_date = '2024-04-04';


-- Matching provider_key wise orders between swclo and fod
-- ====================================================================

-- for one day  and one seller 

select distinct provider_key, sum(total_items)
from staging_all.fact_order_detail fod
where seller_np = 'biz.enstore.com'
and fod.order_date = '2024-04-04'
group by fod.provider_key;


select distinct provider_key from staging_all.fact_order_detail fod
where fod.seller_np = 'biz.enstore.com' and fod.order_date = '2024-04-04';


select cod.provider_key , sum(cod.total_items)  from staging_all.category_level_orders cod
where order_date = '2024-04-04'
and provider_key in (select distinct provider_key from staging_all.fact_order_detail fod
where fod.seller_np = 'biz.enstore.com' and fod.order_date = '2024-04-04')
group by cod.provider_key;


-- for all sellers for one day

select distinct provider_key, sum(total_items)
from staging_all.fact_order_detail fod
where fod.order_date = '2024-04-04'
group by fod.provider_key;


select distinct provider_key from staging_all.fact_order_detail fod
where fod.order_date = '2024-04-04';


select cod.provider_key , sum(cod.total_items)  from staging_all.category_level_orders cod
where order_date = '2024-04-04'
and provider_key in (select distinct provider_key from staging_all.fact_order_detail fod
where fod.order_date = '2024-04-04')
group by cod.provider_key;


-- Matching provider_key wise orders between swclo and fod
-- ====================================================================

select distinct delivery_state , sum(total_items) from fact_order_detail fod
where order_date = '2024-04-04'
group by delivery_state;

select dlo.delivery_state , sum(dlo.total_items)  from staging_all.district_level_orders dlo
where order_date = '2024-04-04'
and delivery_state in (select distinct delivery_state from staging_all.fact_order_detail fod
where fod.order_date = '2024-04-04')
group by dlo.delivery_state;


-- Matching provider_key wise orders between swsclo and fod
-- ====================================================================

select distinct sub_category , sum(total_items) from fact_order_detail fod
where order_date = '2024-04-04'
group by sub_category;

select sclo.sub_category , sum(sclo.total_items)  from staging_all.sub_category_level_orders sclo
where order_date = '2024-04-04'
and sub_category in (select distinct sub_category from staging_all.fact_order_detail fod
where fod.order_date = '2024-04-04')
group by sclo.sub_category;


