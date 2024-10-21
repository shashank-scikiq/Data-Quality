import os
import utils
import re
import sys

import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
from glob import glob
from EXT_ATH import process_date
from dotenv import load_dotenv
import Dir_chk as dc
from FA_Backend.Models.models import engine, meta
from utils import tbl_names

import pyarrow.parquet as pq
import psycopg
from io import StringIO



user = utils.PG_USER
if not user:
    print("Environment not loaded.")
else:
    print("Environment variables are loaded.")


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


def get_raw_results(results):
    final_data = []
    columns = [x["VarCharValue"] for x in results["rows"][0]["Data"]]
    rows = [list(map(lambda field: field.get('VarCharValue', ''), row['Data'])) for row in results['rows'][1:]]
    for data in rows:
        final_data.append(data)
    return pd.DataFrame(columns=columns, data=final_data)


def list_dates(start_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.now().date()
    date_list = []

    while start_date.date() <= end_date:
        date_list.append(start_date.date())
        start_date += timedelta(days=1)
    return date_list


def dump_parquet_to_postgresql(parquet_file_path, table_name, conn_info):
    table = pq.read_table(parquet_file_path)
    df = table.to_pandas()
    try:
        with psycopg.connect(**conn_info) as conn:
            with conn.cursor() as cur:
                buffer = StringIO()
                df.to_csv(buffer, index=False, header=False)
                buffer.seek(0)
                cur.copy("COPY {} FROM STDIN WITH CSV".format(table_name), buffer)
                conn.commit()
    except Exception as e:
        raise e
    else:
        print("Done.")


def exec_sql(conn: str, query: str, tbl_name: list = None):
    try:
        engine = create_engine(conn)
    except Exception as e:
        raise e

    with engine.connect() as db_conn:
        if tbl_name:
            for table in tbl_name:
                print(f"Now Truncating --> {table}")
                try:
                    db_conn.execute(text(query))
                    print(f"Executed Query on {tbl_name}")
                except Exception as e:
                    print(f"Error truncating {tbl_name}: {e}")
                    raise e
        else:
            try:
                db_conn.execute(text(query))
                print(f"Successfully executed the query.")
            except Exception as e:
                print(f"Error executing the query.")
                raise e


def dqEtlMain():
    print("Checking the Target Folder.")
    final_dir = dc.check_create_folders(os.getenv("DQ_DUMP_LOC"))
    print(final_dir)

    print("Checking the DB Connection.")
    try:
        conn=psycopg.connect(utils.conn_info)
    except Exception as db_err:
        raise db_err
    else:
        print("DB is reachable.")
        pg_url = f"postgresql://{utils.PG_USER}:{utils.PG_PASSWD}@{utils.PG_HOST}:{utils.PG_PORT}/{utils.PG_DB}"

    print("Verifying the schema.")
    create_sch = f"""CREATE SCHEMA IF NOT EXISTS "{utils.PG_SCHEMA}" AUTHORIZATION "{utils.PG_USER}"""
    exec_sql(conn=pg_url, query=create_sch)

    print("Creating the Tables.")
    with engine.begin() as conn_obj:
        conn_obj.run_sync(meta.create_all)

    print("Extract the data from DB.")

    final_sql = "".join(read_file("D:\\Work\\git\\Data-Quality\\FA_Backend\\Sql\\base_dim_order_status.sql"))

    for key, value in utils.tbl_names.items():
        try:
            final_sql = re.sub(rf'\b{re.escape(key)}\b', value, final_sql)
        except Exception as e:
            print("Error while replacing the values.")
            print(key, value)
            raise e

    print(final_sql.format(date_val=12))


    print("Load the data in all tables.")

    print("Send Status update.")