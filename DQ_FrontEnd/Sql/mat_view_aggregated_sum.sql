CREATE OR REPLACE VIEW "PG_SCHEMA"."AGG_SUM"
AS SELECT ord_date,
    seller_np,
    total_orders,
    total_canceled_orders,
    null_cans_code + null_cans_dt_time AS canc_metrices,
    total_orders - total_canceled_orders AS completed_orders,
    null_fulfilment_id + null_net_tran_id + null_qty + null_itm_fulfilment_id + null_del_pc + null_created_date_time + null_domain + null_del_cty + null_ord_stats + null_fulfil_status + null_itm_cat + null_cat_cons + null_sell_pincode + null_prov_id + null_itm_id + null_sell_np + null_net_ord_id + null_sell_cty AS sum_missing_cols
   FROM "PG_SCHEMA"."AGG_VIEW" av;