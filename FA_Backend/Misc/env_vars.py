import os
from dotenv import load_dotenv

load_dotenv("../.env")

PG_USER = os.getenv("PG_USERNAME")
PG_PWD = os.getenv("PG_PASSWD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")
ENV_FILE = "../.env"

DQ_TBL = os.getenv("DQ_TABLE")
AGG_VIEW = os.getenv("AGG_VIEW")
AGG_SUM = os.getenv("AGG_SUM")
