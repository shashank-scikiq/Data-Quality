from dotenv import load_dotenv
import os
import sys

try:
    ENV_FILE = os.getenv(".env")
    load_dotenv(ENV_FILE)
except Exception as e:
    raise e
else:
    print("Loaded Env from File.")

# DB Connection Variables
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USERNAME")
PG_PWD = os.getenv("PG_PASSWD")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")

# Schemas and Tables
DQ_TBL = os.getenv("DQ_TABLE")
AGG_VIEW = os.getenv("AGG_VIEW")
AGG_SUM = os.getenv("AGG_SUM")
COL_SUM = os.getenv("COL_SUM")
DIM_ORD_STAT = os.getenv("DIM_ORD_STATUS")
DIM_SELLERS = os.getenv("DIM_SELLERS")
CANC_ORD_STAT = os.getenv("CANC_ORD_STAT")
COMPL_ORD_STAT = os.getenv("COMPL_ORD_STAT")

# Data Sanity
DS_PG_SCHEMA = os.getenv("DB_SCHEMA_SOURCE_DATA_SANITY")
DS_TABLE = os.getenv("DATA_SANITY_TBL")
DS_DB = os.getenv("DS_DB_NAME")
DS_START_DATE = os.getenv("START_DATE")


#  Check Required Environment Variables.
def chk_env_vars():
    required_vars = ["PG_HOST", "PG_PORT",
                     "PG_USERNAME", "PG_PASSWD", "PG_DB",
                     "PG_SCHEMA", "DQ_TABLE", "AGG_VIEW", "AGG_SUM",
                     "COL_SUM"]
    missing_vars = []

    for var in required_vars:
        if var not in os.environ.keys():
            missing_vars.append(var)

    if missing_vars:
        print("Required Environment Variables are missing. ")
        print(missing_vars)
        sys.exit()
    else:
        print("All Required Environment variables are loaded.")


chk_env_vars()
