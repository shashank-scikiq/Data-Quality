import asyncio
import sys

import re
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta, date
from glob import glob
import os

from utils import DQ_TBL, DIM_ORD_STAT, DIM_SELLERS, SQL_FILES
from utils import PG_USER, PG_PASSWD, PG_HOST, PG_PORT, PG_DB, PG_SCHEMA
from utils import START_DATE, DUMP_LOC, tbl_names

from EXT_ATH import process_date

sql_mapping = {
    "dq_main":"base_od_dq_nhm.sql",
    "dim_sellers":"base_dim_sellers.sql",
    "dim_order_status":"base_dim_order_status"
}

