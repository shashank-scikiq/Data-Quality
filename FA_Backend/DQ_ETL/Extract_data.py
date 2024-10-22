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
    "dim_order_status":"base_dim_order_status.sql"
}

conn_str = f"postgresql+psycopg://{PG_USER}:{PG_PASSWD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
to_drop = [DQ_TBL, DIM_ORD_STAT, DIM_SELLERS]


def get_raw_results(results):
    final_data = []
    columns = [x["VarCharValue"] for x in results["rows"][0]["Data"]]
    rows = [list(map(lambda field: field.get('VarCharValue', ''), row['Data'])) for row in results['rows'][1:]]
    for data in rows:
        final_data.append(data)
    return pd.DataFrame(columns=columns, data=final_data)


def list_dates(start_date, period='days'):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.now().date()
    date_list = []

    while start_date.date() <= end_date:
        date_list.append(start_date.date().strftime(format="%Y-%m-%d"))

        if period == 'days':
            start_date += timedelta(days=1)
        elif period == 'months':
            if start_date.month == 12:
                start_date = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.month + 1
                try:
                    start_date = start_date.replace(month=next_month)
                except ValueError:
                    # Handle the cases like transitioning from Jan 31 to Feb
                    start_date = start_date.replace(day=1, month=next_month) + timedelta(days=31)
                    start_date = start_date.replace(day=1)
    return date_list


def read_file(f_name: str) -> str:
    """
    f_name = The file name which needs to be read along with
    the location.

    Returns a list of contents.
    """
    file_contents: list[str] = []
    if os.path.exists(f_name):
        print(f"Found File {f_name}.")
        try:
            with open(f_name, 'r') as f:
                file_contents = f.readlines()
        except Exception as e:
            raise e
        else:
            print("File read successfully.")
    else:
        print("File {} not Found. Exiting. ".format(f_name))
        sys.exit()
    formatted_contents = "".join(file_contents)
    return formatted_contents


def check_create_folders(data_loc: str):
    if os.path.exists(data_loc):
        print("Location Found. Proceeding")
    else:
        print(data_loc, " not found. Exiting.")
        sys.exit()

    dt_today = str(datetime.today().date())
    fold_curr_dt = f"{data_loc}/DATA_QUALITY_{dt_today}"

    if os.path.exists(fold_curr_dt):
        print(f"{fold_curr_dt} already exists for processing.")
        return fold_curr_dt
    else:
        print("Creating folder.")
        print(fold_curr_dt)
        try:
            os.mkdir(fold_curr_dt)
        except Exception as e:
            raise e
        return fold_curr_dt


async def extractData():
    print("Checking the Target Folder.")
    print(DUMP_LOC)
    final_dir = check_create_folders(DUMP_LOC)
    print(final_dir)

    print("Starting the Extract Process.")
    dates_between = list_dates(START_DATE, period="months")

    print(tbl_names)
    for tbl_name in sql_mapping:
        print(f"Processing table {tbl_name}")
        final_sql = "".join(read_file(SQL_FILES+sql_mapping[tbl_name]))
        if final_sql:
            for key, value in tbl_names.items():
                # print(key)
                try:
                    final_sql = re.sub(rf'\b{re.escape(key)}\b', value, final_sql)
                except Exception as e:
                    print("Error while replacing the values.")
                    print(key, value)
                    raise e
            # print(final_sql)
            for date_month in dates_between:
                print(f"Processing {date_month}")
                results = await process_date(tbl_name=tbl_name, date=date_month, raw_query=final_sql.format(date_val = date_month))
                df = get_raw_results(results)
                df.to_parquet(final_dir + f"\\{tbl_name}_{date_month}.parquet", index=False)


if __name__ == "__main__":
    asyncio.run(extractData())