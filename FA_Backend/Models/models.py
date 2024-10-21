from sqlalchemy import create_engine, MetaData, Table, Column, Date, String, BIGINT, INT
from FA_Backend.DQ_ETL import utils as ev

print("The port is ", ev.PG_PORT)
engine = create_engine(f"postgresql+psycopg://{ev.PG_USER}:{ev.PG_PASSWD}@{ev.PG_HOST}:{ev.PG_PORT}/{ev.PG_DB}")
meta = MetaData()
meta.reflect(bind=engine, schema=ev.PG_SCHEMA)

od_dq_base = Table(
    ev.DQ_TBL,
    meta,
    Column("curr_date", Date, nullable=True),
    Column("ord_date", Date, nullable=True),
    Column("null_fulfilment_id", BIGINT, nullable=True),
    Column("null_net_tran_id", BIGINT, nullable=True),
    Column("null_qty", BIGINT, nullable=True),
    Column("null_itm_fulfilment_id", BIGINT, nullable=True),
    Column("null_del_pc", BIGINT, nullable=True),
    Column("null_created_date_time", BIGINT, nullable=True),
    Column("null_cans_code", BIGINT, nullable=True),
    Column("null_cans_dt_time", BIGINT, nullable=True),
    Column("null_ord_stats", BIGINT, nullable=True),
    Column("null_fulfil_status", BIGINT, nullable=True),
    Column("null_itm_cat", BIGINT, nullable=True),
    Column("null_cat_cons", BIGINT, nullable=True),
    Column("null_sell_pincode", BIGINT, nullable=True),
    Column("null_prov_id", BIGINT, nullable=True),
    Column("seller_np", String(255), nullable=True),
    Column("null_itm_id", BIGINT, nullable=True),
    Column("null_sell_np", BIGINT, nullable=True),
    Column("null_net_ord_id", BIGINT, nullable=True),
    Column("null_del_cty", BIGINT, nullable=True),
    Column("null_sell_cty", BIGINT, nullable=True),
    Column("total_orders", BIGINT, nullable=True),
    Column("total_canceled_orders", BIGINT, nullable=True),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_agg_view = Table(
    ev.AGG_VIEW,
    meta,
    Column("ord_date", Date, nullable=False),
    Column("seller_np", String(100), nullable=True),
    Column("total_orders", BIGINT, nullable=False),
    Column("total_canceled_orders", BIGINT, nullable=False),
    Column("null_fulfilment_id", BIGINT, nullable=False),
    Column("null_net_tran_id", BIGINT, nullable=False),
    Column("null_qty", BIGINT, nullable=False),
    Column("null_itm_fulfilment_id", BIGINT, nullable=False),
    Column("null_del_pc", BIGINT, nullable=False),
    Column("null_created_date_time", BIGINT, nullable=False),
    Column("null_domain", BIGINT, nullable=False),
    Column("null_del_cty", BIGINT, nullable=False),
    Column("null_cans_code", BIGINT, nullable=False),
    Column("null_cans_dt_time", BIGINT, nullable=False),
    Column("null_ord_stats", BIGINT, nullable=False),
    Column("null_fulfil_status", BIGINT, nullable=False),
    Column("null_itm_cat", BIGINT, nullable=False),
    Column("null_cat_cons", BIGINT, nullable=False),
    Column("null_sell_pincode", BIGINT, nullable=False),
    Column("null_prov_id", BIGINT, nullable=False),
    Column("null_itm_id", BIGINT, nullable=False),
    Column("null_sell_np", BIGINT, nullable=False),
    Column("null_net_ord_id", BIGINT, nullable=False),
    Column("null_sell_cty", BIGINT, nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_agg_sum = Table(
    ev.AGG_SUM,
    meta,
    Column("ord_date", Date, nullable=False),
    Column("seller_np", String(100), nullable=False),
    Column("total_orders", BIGINT, nullable=False),
    Column("total_canceled_orders", BIGINT, nullable=False),
    Column("canc_metrices", BIGINT, nullable=False),
    Column("completed_orders", BIGINT, nullable=False),
    Column("sum_missing_cols", BIGINT, nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_col_sum = Table(
    ev.COL_SUM,
    meta,
    Column("ord_date", Date, nullable=False),
    Column("seller_np", String(255), nullable=False),
    Column("total_orders", BIGINT, nullable=False),
    Column("total_canceled_orders", BIGINT, nullable=False),
    Column("null_fulfilment_id", BIGINT, nullable=False),
    Column("null_net_tran_id", BIGINT, nullable=False),
    Column("null_qty", BIGINT, nullable=False),
    Column("null_itm_fulfilment_id", BIGINT, nullable=False),
    Column("null_del_pc", BIGINT, nullable=False),
    Column("null_cans_code", BIGINT, nullable=False),
    Column("null_cans_dt_time", BIGINT, nullable=False),
    Column("null_ord_stats", BIGINT, nullable=False),
    Column("null_fulfil_status", BIGINT, nullable=False),
    Column("null_itm_cat", BIGINT, nullable=False),
    Column("null_cat_cons", BIGINT, nullable=False),
    Column("null_sell_pincode", BIGINT, nullable=False),
    Column("null_prov_id", BIGINT, nullable=False),
    Column("null_itm_id", BIGINT, nullable=False),
    Column("null_sell_np", BIGINT, nullable=False),
    Column("null_net_ord_id", BIGINT, nullable=False),
    Column("null_sell_cty", BIGINT, nullable=False),
    Column("null_del_cty", BIGINT, nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_dim_order_status = Table(
    ev.DIM_ORD_STAT,
    meta,
    Column("order_date", Date, nullable=False),
    Column("seller_np", String(255), nullable=True),
    Column("order_status", String(255), nullable=True),
    Column("cancellation_code", String(255), nullable=True),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_dim_sellers = Table(
    ev.DIM_SELLERS,
    meta,
    Column("order_date", Date, nullable=False),
    Column("seller_np", String(255), nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

dq_agg_order_stats = Table(
    ev.AGG_ORD_STATS,
    meta,
    Column("order_date", Date, nullable = False),
    Column("order_status", String(50), nullable = False),
    Column("seller_np", String(255), nullable=True),
    Column("count", INT, nullable=True),
    schema = ev.PG_SCHEMA,
    extend_existing=True
)

ds_data_sanity = Table(
    ev.DS_TABLE,
    meta,
    Column("month", Date, nullable=False),
    Column("sub_domain_name", String(50), nullable=False),
    Column("dashboard", String(255), nullable=False),
    Column("view_name", String(255), nullable=False),
    Column("row_count", BIGINT, nullable=False),
    Column("distinct_order_count", BIGINT, nullable=False),
    Column("row_count_till_last_run_date", BIGINT, nullable=False),
    Column("distinct_order_count_till_last_run_date", BIGINT, nullable=False),
    Column("run_date", Date, nullable=False),
    Column("domain_name", String(100), nullable=False),
    Column("last_run_date", Date, nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)

ds_last_run_date = Table(
    ev.DS_LAST_RUN_DATE,
    meta,
    Column("month", Date, nullable=False),
    Column("NO-OD B2C", INT, nullable=True),
    Column("NO-OD B2B", INT, nullable=True),
    Column("NO-OD GV", INT, nullable=True),
    Column("NO-OD Logistics", INT, nullable=True),
    Column("OD-L1 B2C", INT, nullable=True),
    Column("OD-L1 B2B", INT, nullable=True),
    Column("OD-L1 GV", INT, nullable=True),
    Column("OD-L1 Logistics", INT, nullable=True),
    Column("L1-L2 B2C", INT, nullable=True),
    Column("L1-L2 B2B", INT, nullable=True),
    Column("L1-L2 GV", INT, nullable=True),
    Column("L1-L2 Logistics", INT, nullable=True),
    Column("L2-L3 B2C", INT, nullable=True),
    Column("L2-L3 B2B", INT, nullable=True),
    Column("L2-L3 GV", INT, nullable=True),
    Column("L2-L3 Logistics", INT, nullable=True),
    Column("run_date", Date, nullable=False),
    schema=ev.PG_SCHEMA,
    extend_existing=True
)
