import gspread
import pandas as pd
from datetime import date, datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import create_engine
from pyathena import connect
import psycopg2
import sys
# from DQ_queries_new import *
from queries import get_queries
from dotenv import load_dotenv
import os

start_time = datetime.now()
print(f"Start time: {start_time}")
load_dotenv()

# AWS Athena configuration
REGION_NAME = os.getenv('REGION_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_STAGING_DIR = os.getenv('S3_STAGING_DIR')
DATABASE = os.getenv('DATABASE')
SCHEMA = os.getenv('SCHEMA')
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID.strip('"')

# Selecting cumulative transactions and dates
try:
    athena_conn = connect(
        aws_access_key_id=AWS_ACCESS_KEY_ID, 
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
        s3_staging_dir=S3_STAGING_DIR, 
        region_name=REGION_NAME
    )
    print(athena_conn)
except Exception as e:
    print(f"Error connecting to Athena: {e}")
    athena_conn = None


# Postgres EC2 connection
# DB_HOST_SOURCE = os.getenv('DB_HOST_SOURCE')
DB_HOST_SOURCE = os.getenv('DB_HOST_VPN_SOURCE')
DB_PORT_SOURCE = os.getenv('DB_PORT_SOURCE')
DB_NAME_SOURCE = os.getenv('DB_NAME_SOURCE')
DB_USER_SOURCE = os.getenv('DB_USER_SOURCE')
DB_PASSWORD_SOURCE = os.getenv('DB_PASSWORD_SOURCE')
DB_NAME_TARGET=os.getenv('DB_NAME_TARGET')

# Connection URL
connection_url = f'postgresql+psycopg2://{DB_USER_SOURCE}:{DB_PASSWORD_SOURCE}@{DB_HOST_SOURCE}:{DB_PORT_SOURCE}/{DB_NAME_SOURCE}'
connection_url_t = f'postgresql+psycopg2://{DB_USER_SOURCE}:{DB_PASSWORD_SOURCE}@{DB_HOST_SOURCE}:{DB_PORT_SOURCE}/{DB_NAME_TARGET}'
# print(connection_url)
# print(connection_url_t)

query_run_date="""select max(a."run_date") from public.data_sanity_table a"""
df_run_date=pd.read_sql_query(query_run_date,connection_url_t)
run_date = df_run_date.iloc[0]['max']#.strftime('%Y-%m-%d')
# print("run date is ", run_date)

QUERIES = get_queries(run_date)

engine = create_engine(connection_url)

def read_sql_query_and_format_time(query, conn):
    df = pd.read_sql_query(query, conn)
    df['month'] = pd.to_datetime(df['month'])#.dt.strftime('%b %Y')
    return df


df_logistics_NO= read_sql_query_and_format_time(QUERIES.get('logistics_NO_query', None), athena_conn)
df_B2C_NO= read_sql_query_and_format_time(QUERIES.get('B2C_NO_query', None), athena_conn)
df_B2B_NO= read_sql_query_and_format_time(QUERIES.get('B2B_NO_query', None), athena_conn)
df_GV_NO= read_sql_query_and_format_time(QUERIES.get('GV_NO_query', None), athena_conn)
df_logistics_OD= read_sql_query_and_format_time(QUERIES.get('logistics_OD_query', None), athena_conn)
df_B2C_OD= read_sql_query_and_format_time(QUERIES.get('B2C_OD_query', None), athena_conn)
df_B2B_OD= read_sql_query_and_format_time(QUERIES.get('B2B_OD_query', None), athena_conn)
df_GV_OD= read_sql_query_and_format_time(QUERIES.get('GV_OD_query', None), athena_conn)
df_od_no_validation= read_sql_query_and_format_time(QUERIES.get('OD_NO_validation_query', None), athena_conn)
# Add today's date as run_date
df_L1_B2C= read_sql_query_and_format_time(QUERIES.get('B2C_L1_query', None), engine)
df_L1_B2B= read_sql_query_and_format_time(QUERIES.get('B2B_L1_query', None), engine)
df_L1_GV= read_sql_query_and_format_time(QUERIES.get('GV_L1_query', None), engine)
df_L1_logistics= read_sql_query_and_format_time(QUERIES.get('logistics_L1_query', None), engine)
df_L2_B2C= read_sql_query_and_format_time(QUERIES.get('B2C_L2_query', None), engine)
df_L2_B2B= read_sql_query_and_format_time(QUERIES.get('B2B_L2_query', None), engine)
df_L2_GV= read_sql_query_and_format_time(QUERIES.get('GV_L2_query', None), engine)
df_L2_logistics= read_sql_query_and_format_time(QUERIES.get('logistics_L2_query', None), engine)
df_L3_retail= read_sql_query_and_format_time(QUERIES.get('L3_query_Retail', None), engine)
df_L3_logistics= read_sql_query_and_format_time(QUERIES.get('L3_query_Logistics', None), engine)


df_logistics_NO_LRD= read_sql_query_and_format_time(QUERIES.get('logistics_NO_query_LRD', None), athena_conn)
df_B2C_NO_LRD= read_sql_query_and_format_time(QUERIES.get('B2C_NO_query_LRD', None), athena_conn)
df_B2B_NO_LRD= read_sql_query_and_format_time(QUERIES.get('B2B_NO_query_LRD', None), athena_conn)
df_GV_NO_LRD= read_sql_query_and_format_time(QUERIES.get('GV_NO_query_LRD', None), athena_conn)
df_logistics_OD_LRD= read_sql_query_and_format_time(QUERIES.get('logistics_OD_query_LRD', None), athena_conn)
df_B2C_OD_LRD= read_sql_query_and_format_time(QUERIES.get('B2C_OD_query_LRD', None), athena_conn)
df_B2B_OD_LRD= read_sql_query_and_format_time(QUERIES.get('B2B_OD_query_LRD', None), athena_conn)
df_GV_OD_LRD= read_sql_query_and_format_time(QUERIES.get('GV_OD_query_LRD', None), athena_conn)
df_od_no_validation_LRD= read_sql_query_and_format_time(QUERIES.get('OD_NO_validation_query_LRD', None), athena_conn)
df_L1_B2C_LRD= read_sql_query_and_format_time(QUERIES.get('B2C_L1_query_LRD', None), engine)
df_L1_B2B_LRD= read_sql_query_and_format_time(QUERIES.get('B2B_L1_query_LRD', None), engine)
df_L1_GV_LRD= read_sql_query_and_format_time(QUERIES.get('GV_L1_query_LRD', None), engine)
df_L1_logistics_LRD= read_sql_query_and_format_time(QUERIES.get('logistics_L1_query_LRD', None), engine)
df_L2_B2C_LRD= read_sql_query_and_format_time(QUERIES.get('B2C_L2_query_LRD', None), engine)
df_L2_B2B_LRD= read_sql_query_and_format_time(QUERIES.get('B2B_L2_query_LRD', None), engine)
df_L2_GV_LRD= read_sql_query_and_format_time(QUERIES.get('GV_L2_query_LRD', None), engine)
df_L2_logistics_LRD= read_sql_query_and_format_time(QUERIES.get('logistics_L2_query_LRD', None), engine)

df_combined_athena=pd.concat([
    df_logistics_NO, df_B2C_NO, df_B2B_NO, df_GV_NO, df_logistics_OD, df_B2C_OD, df_B2B_OD, 
    df_GV_OD, df_L1_B2B, df_L1_B2C, df_L1_GV, df_L1_logistics, df_L2_B2B, df_L2_B2C, df_L2_GV, 
    df_L2_logistics, df_L3_logistics, df_L3_retail, df_od_no_validation, df_logistics_NO_LRD, 
    df_B2C_NO_LRD, df_B2B_NO_LRD, df_GV_NO_LRD, df_logistics_OD_LRD, df_B2C_OD_LRD,df_B2B_OD_LRD,
    df_GV_OD_LRD,df_L1_B2B_LRD,df_L1_B2C_LRD,df_L1_GV_LRD,df_L1_logistics_LRD,df_L2_B2B_LRD,
    df_L2_B2C_LRD,df_L2_GV_LRD,
    df_L2_logistics_LRD,df_od_no_validation_LRD
], ignore_index=True)

df_combined_athena['run_date'] = date.today()
today = date.today()


df_combined_athena=df_combined_athena.sort_values(by=['month','domain_name'], ascending=False)


column_list = [
    column for column in df_combined_athena.columns.tolist() 
    if column not in [
        'distinct_order_count', 'row_count', 'distinct_order_count_till_last_run_date', 'row_count_till_last_run_date'
        ]
    ]

combined_df = df_combined_athena.groupby(column_list).agg(
    {
        'month': 'max',
        'sub_domain_name': 'max',
        'dashboard': 'max',
        'view_name': 'max',
       'row_count': 'max', 
       'distinct_order_count': 'max', 
       'row_count_till_last_run_date': 'max',
       'distinct_order_count_till_last_run_date': 'max', 
       'run_date': 'max',
       'domain_name': 'max'
    }
)

combined_df['last_run_date']=run_date

engine_t = create_engine(connection_url_t)
combined_df.to_sql('data_sanity_table',engine_t,if_exists='append', index=False, schema='public')

print("Variance Data ingested into the data_variance_report table")



