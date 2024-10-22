import os
from dotenv import load_dotenv
import re
import sys

try:
	env_file="../.env"
	load_dotenv(env_file)
except Exception as e:
	raise e
else:
	print("Env loaded in utils.")

aws_region = os.getenv('AWS_REGION')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
ATH_DB = os.getenv('ATH_DB')
S3_LOCATION = os.getenv('S3_STAGING_DIR')
BASE_TABLE = os.getenv("nhm_order_fulfillment_subset_v1")

# Target Postgresql params
# ==================================================
PG_USER = os.getenv("PG_USERNAME")
PG_PASSWD = os.getenv("PG_PASSWD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")

# Postgresql Table Names
# ==================================================
DQ_TBL = os.getenv("DQ_TABLE")
AGG_VIEW = os.getenv("AGG_VIEW")
AGG_SUM = os.getenv("AGG_SUM")
COL_SUM = os.getenv("COL_SUM")
DIM_ORD_STAT = os.getenv("DIM_ORD_STAT")
DIM_SELLERS = os.getenv("DIM_SELLERS")
AGG_ORD_STATS = os.getenv("AGG_ORD_STATS")
DS_TABLE = os.getenv("DS_TABLE")
DS_LAST_RUN_DATE = os.getenv("DS_LAST_RUN_DATE")
DATA_SANITY_TBL = os.getenv("DATA_SANITY_TBL")

# Misc Variables
# ==================================================
file_loc = os.getenv("DQ_DUMP_LOC")

tbl_names = {
	"DQ_TBL" : os.getenv("DQ_TBL"),
	"AGG_VIEW" : os.getenv("AGG_VIEW"),
	"AGG_SUM" : os.getenv("AGG_SUM"),
	"COL_SUM" : os.getenv("COL_SUM"),
	"DIM_ORD_STAT" : os.getenv("DIM_ORD_STAT"),
	"DIM_SELLERS" : os.getenv("DIM_SELLERS"),
	"AGG_ORD_STATS" : os.getenv("AGG_ORD_STATS"),
	"DS_TABLE" : os.getenv("DATA_SANITY_TBL"),
	"DS_LAST_RUN_DATE" : os.getenv("DS_LAST_RUN_DATE"),
	"ATH_DB": os.getenv("ATH_DB"),
	"BASE_TABLE": os.getenv("BASE_TABLE"),
	"ATH_SCHEMA": os.getenv("ATH_SCHEMA"),
}

SQL_FILES = os.getenv("SCRIPT_LOC")
START_DATE = os.getenv("START_DATE")
DUMP_LOC = os.getenv("DQ_DUMP_LOC")

# Connection information
conn_info = {
    'dbname': PG_DB,
    'user': PG_USER,
    'password': PG_PASSWD,
    'host': PG_HOST,
    'port': PG_PORT
}


def check_env_vars():
	pass

