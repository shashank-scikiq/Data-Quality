import asyncio
import sys
import re
import pandas as pd
from datetime import datetime, timedelta
import os
import pathlib

current_path = pathlib.Path(__file__).resolve()
project_root = current_path.parent.parent
sys.path.append(str(project_root))

from Toolkit.utils import START_DATE, DUMP_LOC, tbl_names, SQL_FILES
from .EXT_ATH import process_date

sql_mapping = {
    "dq_main": "base_od_dq_nhm.sql",
    "dim_sellers": "base_dim_sellers.sql",
    "dim_order_status": "base_dim_order_status.sql"
}


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
        date_list.append((start_date.date()).strftime(format="%Y-%m-%d"))

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
                    start_date = start_date.replace(day=1, month=next_month) + timedelta(days=31)
                    start_date = start_date.replace(day=1)
    return date_list


def read_file(f_name: str) -> str:
    file_contents: list[str] = []
    if os.path.exists(f_name):
        try:
            with open(f_name, 'r') as f:
                file_contents = f.readlines()
        except Exception as e:
            raise e
    else:
        print(f"File {f_name} not Found. Exiting.")
        sys.exit()
    return "".join(file_contents)


def check_create_folders(data_loc: str):
    if not os.path.exists(data_loc):
        print(f"{data_loc} not found. Exiting.")
        sys.exit()

    dt_today = str(datetime.today().date())
    fold_curr_dt = f"{data_loc}/DATA_QUALITY_{dt_today}"

    if not os.path.exists(fold_curr_dt):
        try:
            os.mkdir(fold_curr_dt)
        except Exception as e:
            raise e
    return fold_curr_dt


async def process_table_for_month(tbl_name, date_month, final_sql, final_dir):
    try:
        results = await process_date(
            tbl_name=tbl_name,
            date=date_month,
            raw_query=final_sql.format(date_val=date_month)
        )
        df = get_raw_results(results)
        file_path = os.path.join(final_dir, f"{tbl_name}_{date_month}.parquet")
        df.to_parquet(file_path, index=False)
        print(f"Saved {tbl_name} for {date_month} to {file_path}")
    except Exception as e:
        print(f"Error processing {tbl_name} for {date_month}: {e}")


async def process_table(tbl_name, dates_between, final_dir):
    final_sql = read_file(SQL_FILES + sql_mapping[tbl_name])
    for key, value in tbl_names.items():
        try:
            final_sql = re.sub(rf'\b{re.escape(key)}\b', value, final_sql)
        except Exception as e:
            print(f"Error replacing placeholders in SQL for {tbl_name}: {e}")
            raise e

    tasks = [
        process_table_for_month(tbl_name, date_month, final_sql, final_dir)
        for date_month in dates_between
    ]
    await asyncio.gather(*tasks)


async def dataDump():
    print("Checking the Target Folder.")
    final_dir = check_create_folders(DUMP_LOC)

    print("Starting the Extract Process.")
    dates_between = list_dates(START_DATE, period="months")

    tasks = [
        process_table(tbl_name, dates_between, final_dir)
        for tbl_name in sql_mapping
    ]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(dataDump())