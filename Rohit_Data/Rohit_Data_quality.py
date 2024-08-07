import gspread
import pandas as pd
from datetime import date, datetime
from sqlalchemy import create_engine
from pyathena import connect
from sqlalchemy import create_engine
import psycopg2
import sys
# from DQ_queries_new import *
from DQ_queries import *
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
    athena_conn = connect(aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, s3_staging_dir=S3_STAGING_DIR, region_name=REGION_NAME)
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
print(connection_url)
print(connection_url_t)
query_run_date="""select max(a."Run_date") from public.data_quality_report a"""
df_run_date=pd.read_sql_query(query_run_date,connection_url_t)
run_date = df_run_date.iloc[0]['max']#.strftime('%Y-%m-%d')
print(run_date)
engine = create_engine(connection_url)
def read_sql_query_and_format_time(query, conn):
    df = pd.read_sql_query(query, conn)
    df['month'] = pd.to_datetime(df['month'])#.dt.strftime('%b %Y')
    return df
df_logistics_NO= read_sql_query_and_format_time(logistics_NO_query, athena_conn)
df_B2C_NO= read_sql_query_and_format_time(B2C_NO_query, athena_conn)
df_B2B_NO= read_sql_query_and_format_time(B2B_NO_query, athena_conn)
df_GV_NO= read_sql_query_and_format_time(GV_NO_query, athena_conn)
df_logistics_OD= read_sql_query_and_format_time(logistics_OD_query, athena_conn)
df_B2C_OD= read_sql_query_and_format_time(B2C_OD_query, athena_conn)
df_B2B_OD= read_sql_query_and_format_time(B2B_OD_query, athena_conn)
df_GV_OD= read_sql_query_and_format_time(GV_OD_query, athena_conn)
df_od_no_validation= read_sql_query_and_format_time(OD_NO_validation_query, athena_conn)
# Add today's date as run_date
df_L1_B2C= read_sql_query_and_format_time(B2C_L1_query, engine)
df_L1_B2B= read_sql_query_and_format_time(B2B_L1_query, engine)
df_L1_GV= read_sql_query_and_format_time(GV_L1_query, engine)
df_L1_logistics= read_sql_query_and_format_time(logistics_L1_query, engine)
df_L2_B2C= read_sql_query_and_format_time(B2C_L2_query, engine)
df_L2_B2B= read_sql_query_and_format_time(B2B_L2_query, engine)
df_L2_GV= read_sql_query_and_format_time(GV_L2_query, engine)
df_L2_logistics= read_sql_query_and_format_time(logistics_L2_query, engine)
df_L3_retail= read_sql_query_and_format_time(L3_query_Retail, engine)
df_L3_logistics= read_sql_query_and_format_time(L3_query_Logistics, engine)



logistics_L1_query_LRD_n=logistics_L1_query_LRD.format(run_date=run_date)
logistics_NO_query_LRD_n= logistics_NO_query_LRD.format(run_date=run_date)
logistics_L2_query_LRD_n= logistics_L2_query_LRD.format(run_date=run_date)
logistics_OD_query_LRD_n= logistics_OD_query_LRD.format(run_date=run_date)
B2B_L1_query_LRD_n= B2B_L1_query_LRD.format(run_date=run_date)
B2B_L2_query_LRD_n= B2B_L2_query_LRD.format(run_date=run_date)
B2B_NO_query_LRD_n= B2B_NO_query_LRD.format(run_date=run_date)
B2B_OD_query_LRD_n= B2B_OD_query_LRD.format(run_date=run_date)
B2C_L1_query_LRD_n= B2C_L1_query_LRD.format(run_date=run_date)
B2C_L2_query_LRD_n= B2C_L2_query_LRD.format(run_date=run_date)     
B2C_NO_query_LRD_n= B2C_NO_query_LRD.format(run_date=run_date)
B2C_OD_query_LRD_n= B2C_OD_query_LRD.format(run_date=run_date)
GV_L1_query_LRD_n= GV_L1_query_LRD.format(run_date=run_date)
GV_L2_query_LRD_n= GV_L2_query_LRD.format(run_date=run_date)
GV_NO_query_LRD_n= GV_NO_query_LRD.format(run_date=run_date)
GV_OD_query_LRD_n= GV_OD_query_LRD.format(run_date=run_date)
OD_NO_validation_query_LRD_n=OD_NO_validation_query_LRD.format(run_date=run_date)

df_logistics_NO_LRD= read_sql_query_and_format_time(logistics_NO_query_LRD_n, athena_conn)
df_B2C_NO_LRD= read_sql_query_and_format_time(B2C_NO_query_LRD_n, athena_conn)
df_B2B_NO_LRD= read_sql_query_and_format_time(B2B_NO_query_LRD_n, athena_conn)
df_GV_NO_LRD= read_sql_query_and_format_time(GV_NO_query_LRD_n, athena_conn)
df_logistics_OD_LRD= read_sql_query_and_format_time(logistics_OD_query_LRD_n, athena_conn)
df_B2C_OD_LRD= read_sql_query_and_format_time(B2C_OD_query_LRD_n, athena_conn)
df_B2B_OD_LRD= read_sql_query_and_format_time(B2B_OD_query_LRD_n, athena_conn)
df_GV_OD_LRD= read_sql_query_and_format_time(GV_OD_query_LRD_n, athena_conn)
df_od_no_validation_LRD= read_sql_query_and_format_time(OD_NO_validation_query_LRD_n, athena_conn)
df_L1_B2C_LRD= read_sql_query_and_format_time(B2C_L1_query_LRD_n, engine)
df_L1_B2B_LRD= read_sql_query_and_format_time(B2B_L1_query_LRD_n, engine)
df_L1_GV_LRD= read_sql_query_and_format_time(GV_L1_query_LRD_n, engine)
df_L1_logistics_LRD= read_sql_query_and_format_time(logistics_L1_query_LRD_n, engine)
df_L2_B2C_LRD= read_sql_query_and_format_time(B2C_L2_query_LRD_n, engine)
df_L2_B2B_LRD= read_sql_query_and_format_time(B2B_L2_query_LRD_n, engine)
df_L2_GV_LRD= read_sql_query_and_format_time(GV_L2_query_LRD_n, engine)
df_L2_logistics_LRD= read_sql_query_and_format_time(logistics_L2_query_LRD_n, engine)



df_combined_athena=pd.concat([df_logistics_NO,df_B2C_NO,df_B2B_NO,df_GV_NO,df_logistics_OD,df_B2C_OD,df_B2B_OD,df_GV_OD,df_L1_B2B,df_L1_B2C,df_L1_GV,df_L1_logistics,df_L2_B2B,df_L2_B2C,df_L2_GV,df_L2_logistics,df_L3_logistics,df_L3_retail,df_od_no_validation,df_logistics_NO_LRD,df_B2C_NO_LRD,df_B2B_NO_LRD,df_GV_NO_LRD,df_logistics_OD_LRD,df_B2C_OD_LRD,df_B2B_OD_LRD,df_GV_OD_LRD,df_L1_B2B_LRD,df_L1_B2C_LRD,df_L1_GV_LRD,df_L1_logistics_LRD,df_L2_B2B_LRD,df_L2_B2C_LRD,df_L2_GV_LRD,df_L2_logistics_LRD,df_od_no_validation_LRD], ignore_index=True)
df_combined_athena['Run_date'] = date.today()
today = date.today()


df_combined_athena=df_combined_athena.sort_values(by=['month','domain_name'], ascending=False)
df_combined_athena.to_excel(f"C:\\Users\\Rohit Singh\\Desktop\\ONDC\\OD\\WebScraping\\DQ_athena_{today}.xlsx")


end_time = datetime.now()
print(f"Report generated in time : {end_time - start_time}")
# df_combined_athena=pd.read_csv("C:\\Users\\Rohit Singh\\Desktop\\ONDC\\OD\\data_quality_report_202407161618.csv",parse_dates=['month','Run_date'])
df_combined_athena=df_combined_athena.fillna(0)
# # Convert the 'Run_date' column to datetime
# df_combined_athena['Run_date'] = pd.to_datetime(df_combined_athena['Run_date'])

# # Format the 'Run_date' column to 'YYYY-MM-DD'
df_combined_athena['Run_date'] = df_combined_athena['Run_date'].dt.strftime('%Y-%m-%d')
# grouped = df_combined_athena.groupby(['month', 'domain_name', 'dashboard','Run_date'])['distinct_order_count'].sum().reset_index()

grouped = df_combined_athena.groupby(['month', 'domain_name', 'dashboard', 'Run_date'])['distinct_order_count'].sum().reset_index()

# Define the mappings for Base Diff
base_diff_pairs = {
    'NO-OD': ('NO_with_base_query', 'OD_with_base_query'),
    'OD-L1': ('OD_with_base_query', 'OD_with_L1_query'),
    'L1-L2': ('OD_with_L1_query', 'OD_with_L2_query'),
    'L2-L3': ('OD_with_L2_query', 'OD_with_L3_query')
}

# Initialize an empty list to store the rows for the first table
rows = []

# Iterate over each unique combination of month, domain_name, and Run_date
for month in grouped['month'].unique():
    for run_date in grouped[grouped['month'] == month]['Run_date'].unique():
        for domain_name in grouped[grouped['month'] == month]['domain_name'].unique():
            for base_diff, (start, end) in base_diff_pairs.items():
                try:
                    start_count = grouped[(grouped['month'] == month) & (grouped['Run_date'] == run_date) & (grouped['domain_name'] == domain_name) & (grouped['dashboard'] == start)]['distinct_order_count'].values[0]
                    end_count = grouped[(grouped['month'] == month) & (grouped['Run_date'] == run_date) & (grouped['domain_name'] == domain_name) & (grouped['dashboard'] == end)]['distinct_order_count'].values[0]
                    diff_count = start_count - end_count
                    
                    # Calculate % Difference
                    if end_count != 0:
                        percent_diff = (diff_count / start_count) * 100
                    else:
                        percent_diff = 0.0  # Handle division by zero scenario
                    
                    # Round off to one decimal place
                    percent_diff = round(percent_diff, 1)
                    
                    # Create a row for the current combination
                    rows.append({
                        'Month': month,
                        'Base Diff': base_diff,
                        'Domain': domain_name,
                        'Difference': diff_count,
                        'Run_date': run_date,
                        '% Difference': percent_diff
                    })
                except IndexError:
                    # Handle case where start or end dashboard is not found in the current month, Run_date, and domain_name
                    continue

# Create a new DataFrame for the first table
first_table_df = pd.DataFrame(rows)
print(first_table_df)
# first_table_df.to_excel("C:\\Users\\Rohit Singh\\Desktop\\ONDC\\OD\\Data_variance_SR.xlsx")

# Save the results to an Excel file
# first_table_df.to_excel(f"C:\\Users\\Rohit Singh\\Desktop\\ONDC\\OD\\WebScraping\\DQ_variance_{date.today()}.xlsx", index=False)

print("Variance calculations saved to Excel file")

engine_t = create_engine(connection_url_t)
# engine_t = create_engine(connection_url_t)
df_combined_athena.to_sql('data_quality_report',engine_t,if_exists='append', index=False, schema='public')
first_table_df.to_sql('data_variance_report',engine_t,if_exists='append', index=False, schema='public')
print("Variance Data ingested into the data_variance_report table")
