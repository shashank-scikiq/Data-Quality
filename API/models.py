import os
import env_vars as ev
from sqlalchemy import create_engine, MetaData, Table, Column, Date, String, BIGINT
from dotenv import load_dotenv

load_dotenv(ev.ENV_FILE)

engine = create_engine(f"postgresql+psycopg://{ev.db_user}:{ev.db_pwd}@{ev.db_host}:{ev.db_port}/{ev.db_instance}")
meta = MetaData()
meta.reflect(bind=engine, schema=f"{ev.db_schema}")

od_dq_base = Table(
	ev.dq_table,
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
	schema=ev.db_schema,
	extend_existing=True
)

dq_agg_view = Table(
	ev.agg_view,
	meta,
	Column("ord_date", Date, nullable=False),
	Column("seller_np", String(100), nullable=True),
	Column("total_orders", BIGINT, nullable=False),
	Column("total_canceled_orders",BIGINT , nullable=False),
    Column("null_fulfilment_id",BIGINT , nullable=False),
    Column("null_net_tran_id", BIGINT, nullable=False),
    Column("null_qty",BIGINT , nullable=False),
    Column("null_itm_fulfilment_id",BIGINT , nullable=False),
    Column("null_del_pc",BIGINT , nullable=False),
    Column("null_created_date_time", BIGINT, nullable=False),
    Column("null_domain",BIGINT , nullable=False),
    Column("null_del_cty",BIGINT , nullable=False),
    Column("null_cans_code",BIGINT , nullable=False),
    Column("null_cans_dt_time",BIGINT , nullable=False),
    Column("null_ord_stats",BIGINT , nullable=False),
    Column("null_fulfil_status", BIGINT, nullable=False),
    Column("null_itm_cat",BIGINT , nullable=False),
    Column("null_cat_cons",BIGINT , nullable=False),
    Column("null_sell_pincode",BIGINT , nullable=False),
    Column("null_prov_id", BIGINT, nullable=False),
    Column("null_itm_id", BIGINT, nullable=False),
    Column("null_sell_np",BIGINT , nullable=False),
    Column("null_net_ord_id", BIGINT, nullable=False),
    Column("null_sell_cty", BIGINT, nullable=False),
    schema=ev.db_schema,
    extend_existing=True
)

dq_agg_sum = Table(
	ev.agg_sum,
	meta,
	Column("ord_date",Date, nullable=False),
    Column("seller_np",String(100), nullable=False),
    Column("total_orders", BIGINT, nullable=False),
    Column("total_canceled_orders",BIGINT, nullable=False),
    Column("canc_metrices", BIGINT, nullable=False),
    Column("missing_total_base", BIGINT, nullable=False),
    Column("missing_from_total", BIGINT, nullable=False),
    schema=ev.db_schema,
    extend_existing=True
)
