import os

from sqlalchemy import create_engine, MetaData, Table, Column, Date, String, BIGINT
from dotenv import load_dotenv

try:
	load_dotenv(".env")
except Exception as e:
	print(e.args[0])
else:
	print("Loaded Environment Variables Successfully")

db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_user = os.getenv("POSTGRES_USER")
db_pwd = os.getenv("POSTGRES_PASSWORD")
db_instance = os.getenv("POSTGRES_DB")
db_schema = os.getenv("POSTGRES_SCHEMA")
db_table = os.getenv("OD_DQ_TBL")

engine = create_engine(f"postgresql+psycopg://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_instance}")
meta = MetaData()
meta.reflect(bind=engine, schema=f"{db_schema}")

od_dq = Table(
	db_table,
	meta,
	Column("curr_date", Date, nullable=True),
	Column("ord_date", Date, nullable=True),
	Column("seller_np", String(255), nullable=True),
	Column("null_fulfilment_id", BIGINT, nullable=True),
	Column("null_net_tran_id", BIGINT, nullable=True),
	Column("null_qty", BIGINT, nullable=True),
	Column("null_itm_fulfilment_id", BIGINT, nullable=True),
	Column("null_del_pc", BIGINT, nullable=True),
	Column("null_created_date_time", BIGINT, nullable=True),
	Column("null_domain", BIGINT, nullable=True),
	Column("null_del_cty", BIGINT, nullable=True),
	Column("null_cans_code", BIGINT, nullable=True),
	Column("null_cans_dt_time", BIGINT, nullable=True),
	Column("null_ord_stats", BIGINT, nullable=True),
	Column("null_fulfil_status", BIGINT, nullable=True),
	Column("null_itm_cat", BIGINT, nullable=True),
	Column("null_cat_cons", BIGINT, nullable=True),
	Column("null_sell_pincode", BIGINT, nullable=True),
	Column("null_prov_id", BIGINT, nullable=True),
	Column("null_itm_id", BIGINT, nullable=True),
	Column("null_sell_np", BIGINT, nullable=True),
	Column("null_net_ord_id", BIGINT, nullable=True),
	Column("null_sell_cty", BIGINT, nullable=True),
	Column("total_orders", BIGINT, nullable=True),
	Column("total_canceled_orders", BIGINT, nullable=True),
	schema=db_schema,
	extend_existing=True
)


def check_envs(env_vars):
	for var in env_vars:
		if var not in os.environ:
			raise KeyError(f"Environment variable '{var}' is not loaded.")


def run_stmt(to_run, cnt=0):
	stmt = (
		to_run
	)
	with engine.connect() as conn:
		if cnt > 0:
			result = conn.execute(stmt).fetchmany(cnt)
		else:
			result = conn.execute(stmt).fetchall()
	return result


if __name__ == "__main__":
	required_env_vars = ["POSTGRES_HOST", "POSTGRES_PORT",
						 "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
						 "POSTGRES_SCHEMA", "OD_DQ_TABLE"]
	try:
		check_envs(required_env_vars)
		print("All required environment variables are loaded.")
	except KeyError as e:
		print(f"Error: {e}")

	engine.dispose()
