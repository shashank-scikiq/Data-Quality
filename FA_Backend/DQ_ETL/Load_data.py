import asyncio
import sys
import os
from glob import glob

import pandas as pd
import re

from FA_Backend.Misc.env_vars import AGG_VIEW
from utils import PG_SCHEMA, PG_USER, tbl_names, SQL_FILES
from sqlalchemy import create_engine, text
from FA_Backend.Models.models import engine, meta, od_dq_base, dq_dim_sellers, dq_dim_order_status
from FA_Backend.Models.models import conn_str


file_mapping = {
    "dq_main": od_dq_base,
    "dim_sellers": dq_dim_sellers,
    "dim_order_status": dq_dim_order_status
}


def exec_sql(db_engine, query: str, tbl_name: list = None):
    with db_engine.connect() as db_conn:
        if tbl_name:
            for table in tbl_name:
                print(f"Now Truncating --> {table}")
                try:
                    db_conn.execute(text(query))
                    db_conn.commit()
                except Exception as e:
                    print(f"Error truncating {table}: {e}")
                    raise e
                else:
                    print(f"Executed Query on {table}")
                finally:
                    db_conn.close()
        else:
            try:
                db_conn.execute(text(query))
                db_conn.commit()
            except Exception as e:
                print("Error executing the query.")
                raise e
            else:
                print("Successfully executed the query.")
            finally:
                db_conn.close()


def readCleanQuery(sql_query:str):
    final_sql = sql_query
    for key, value in tbl_names.items():
        print(key, value)
        try:
            final_sql = re.sub(rf'\b{re.escape(key)}\b', value, final_sql)
        except Exception as e:
            print("Error while replacing the values.")
            print(key, value)
            raise e
    return final_sql


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


def convertDateColumns(df: pd.DataFrame) -> pd.DataFrame:
    if "curr_date" in df.columns:
        df["curr_date"] = pd.to_datetime(df["curr_date"], format="%Y-%m-%d").dt.date
    if "ord_date" in df.columns:
        df["ord_date"] = pd.to_datetime(df["ord_date"], format="%Y-%m-%d").dt.date
    if "order_date" in df.columns:
        df["order_date"] = pd.to_datetime(df["order_date"], format="%Y-%m-%d").dt.date
    if "null_domain" in df.columns:
        df = df.drop(columns="null_domain")
    for col in df.columns:
        if col not in ["curr_date", "ord_date", "seller_np", "order_date", "order_status", "cancellation_code"]:
            if df[col].dtype != 'int64':
                df[col] = df[col].astype(int)
    return df


async def dqLoadDb(src_folder: str):
    print("Checking the Source Folder.")
    if os.path.exists(src_folder):
        print("Found Source file location.")
    else:
        print(f"{src_folder} not found. Exiting.")
        sys.exit()

    print("Verifying the schema.")
    create_sch = f"""CREATE SCHEMA IF NOT EXISTS "{PG_SCHEMA}" AUTHORIZATION "{PG_USER}";"""
    print(create_sch)
    exec_sql(db_engine=engine, query=create_sch)

    print("Cleaning the existing tables.")
    with engine.connect() as conn_obj:
        try:
            meta.drop_all(bind=engine)
            conn_obj.commit()
        except Exception as e:
            print(f"Error dropping tables: {e}")
            raise e

    print("Creating the tables again.")
    with engine.begin() as conn_obj:
        try:
            meta.create_all(bind=engine)
            conn_obj.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise e

    print("Reading the raw files.")
    df_dq_main = pd.read_parquet(glob(src_folder + "/*dq_main*"))
    df_dim_sellers = pd.read_parquet(glob(src_folder + "/*dim_sellers*"))
    df_ord_status = pd.read_parquet(glob(src_folder + "/*order_status*"))

    print("Creating the dataframes.")
    df_dq_main = convertDateColumns(df_dq_main)
    df_dim_sellers = convertDateColumns(df_dim_sellers)
    df_ord_status = convertDateColumns(df_ord_status)

    print("Loading the data in the dimension tables.")
    df_dq_main.to_sql(
        name="od_dq_nhm",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )
    df_dim_sellers.to_sql(
        name="dim_sellers",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )
    df_ord_status.to_sql(
        name="dim_order_status",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )


    print("Executing the rest of the tables.")

    print("Creating Aggregated View")
    df_agg_view = df_dq_main.groupby(['ord_date', 'seller_np']).agg(
        total_orders=('total_orders', 'sum'),
        total_canceled_orders=('total_canceled_orders', 'sum'),
        null_fulfilment_id=('null_fulfilment_id', 'sum'),
        null_net_tran_id=('null_net_tran_id', 'sum'),
        null_qty=('null_qty', 'sum'),
        null_itm_fulfilment_id=('null_itm_fulfilment_id', 'sum'),
        null_del_pc=('null_del_pc', 'sum'),
        null_created_date_time=('null_created_date_time', 'sum'),
        null_del_cty=('null_del_cty', 'sum'),
        null_cans_code=('null_cans_code', 'sum'),
        null_cans_dt_time=('null_cans_dt_time', 'sum'),
        null_ord_stats=('null_ord_stats', 'sum'),
        null_fulfil_status=('null_fulfil_status', 'sum'),
        null_itm_cat=('null_itm_cat', 'sum'),
        null_cat_cons=('null_cat_cons', 'sum'),
        null_sell_pincode=('null_sell_pincode', 'sum'),
        null_prov_id=('null_prov_id', 'sum'),
        null_itm_id=('null_itm_id', 'sum'),
        null_sell_np=('null_sell_np', 'sum'),
        null_net_ord_id=('null_net_ord_id', 'sum'),
        null_sell_cty=('null_sell_cty', 'sum')
    ).reset_index()
    df_agg_view = convertDateColumns(df_agg_view)
    df_agg_view.to_sql(
        name="aggregated_view",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )

    print("Creating aggregated sum")
    df_agg_sum = df_agg_view[["ord_date", "seller_np", "total_orders", "total_canceled_orders"]]
    df_agg_sum.loc[:, ['canc_metrices']] = df_agg_view['null_cans_code'] + df_agg_view['null_cans_dt_time']
    df_agg_sum.loc[:, ['completed_orders']] = df_agg_view['total_orders'] - df_agg_view['total_canceled_orders']
    df_agg_sum.loc[:, ['sum_missing_cols']] = (
            df_agg_view['null_fulfilment_id'] +
            df_agg_view['null_net_tran_id'] +
            df_agg_view['null_qty'] +
            df_agg_view['null_itm_fulfilment_id'] +
            df_agg_view['null_del_pc'] +
            df_agg_view['null_created_date_time'] +
            df_agg_view['null_del_cty'] +
            df_agg_view['null_ord_stats'] +
            df_agg_view['null_fulfil_status'] +
            df_agg_view['null_itm_cat'] +
            df_agg_view['null_cat_cons'] +
            df_agg_view['null_sell_pincode'] +
            df_agg_view['null_prov_id'] +
            df_agg_view['null_itm_id'] +
            df_agg_view['null_sell_np'] +
            df_agg_view['null_net_ord_id'] +
            df_agg_view['null_sell_cty']
    )

    df_agg_sum.to_sql(
        name="aggregated_sum",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )

    print("Aggregated Order Status")
    df_agg_ord_stats = df_ord_status.groupby(['order_date', 'order_status', 'seller_np']).agg(
        count=('order_status', 'count')).reset_index()
    df_agg_ord_stats = df_agg_ord_stats.sort_values(by=['order_date', 'seller_np'], ascending=[False, True],
                                                    ignore_index=True)
    df_agg_ord_stats = convertDateColumns(df_agg_ord_stats)
    df_agg_ord_stats.to_sql(
        name="agg_order_stats",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )


    print("Column Sum")
    df_agg_col_sum = df_agg_view.groupby(['ord_date', 'seller_np']).agg(
        total_orders=('total_orders', 'sum'),
        total_canceled_orders=('total_canceled_orders', 'sum'),
        null_fulfilment_id=('null_fulfilment_id', 'sum'),
        null_net_tran_id=('null_net_tran_id', 'sum'),
        null_qty=('null_qty', 'sum'),
        null_itm_fulfilment_id=('null_itm_fulfilment_id', 'sum'),
        null_del_pc=('null_del_pc', 'sum'),
        null_cans_code=('null_cans_code', 'sum'),
        null_cans_dt_time=('null_cans_dt_time', 'sum'),
        null_ord_stats=('null_ord_stats', 'sum'),
        null_fulfil_status=('null_fulfil_status', 'sum'),
        null_itm_cat=('null_itm_cat', 'sum'),
        null_cat_cons=('null_cat_cons', 'sum'),
        null_sell_pincode=('null_sell_pincode', 'sum'),
        null_prov_id=('null_prov_id', 'sum'),
        null_itm_id=('null_itm_id', 'sum'),
        null_sell_np=('null_sell_np', 'sum'),
        null_net_ord_id=('null_net_ord_id', 'sum'),
        null_sell_cty=('null_sell_cty', 'sum'),
        null_del_cty=('null_del_cty', 'sum')
    ).reset_index()

    df_agg_col_sum = df_agg_col_sum.sort_values(by=['ord_date', 'seller_np'], ascending=[False, True])
    df_agg_col_sum = convertDateColumns(df_agg_col_sum)
    df_agg_col_sum.to_sql(
        name="col_sum",
        con=conn_str,
        index=False,
        if_exists='append',
        schema=PG_SCHEMA
    )


if __name__ == "__main__":
    asyncio.run(dqLoadDb("D:\\DATA_DUMP\\DATA_QUALITY\\DATA_QUALITY_2024-10-22\\"))
