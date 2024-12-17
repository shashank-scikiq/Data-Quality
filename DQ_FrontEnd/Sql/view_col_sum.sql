CREATE OR REPLACE VIEW "PG_SCHEMA"."COL_SUM"
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
   FROM "PG_SCHEMA"."AGG_VIEW"
  GROUP BY ord_date, seller_np
  ORDER BY ord_date DESC, seller_np;