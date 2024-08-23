import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv()

DB_HOST_SOURCE = os.getenv('DB_HOST_VPN_SOURCE')
DB_PORT_SOURCE = os.getenv('DB_PORT_SOURCE')
DB_NAME_SOURCE = os.getenv('DB_NAME_TARGET')
DB_USER_SOURCE = os.getenv('DB_USER_SOURCE')
DB_PASSWORD_SOURCE = os.getenv('DB_PASSWORD_SOURCE')
DB_SCHEMA_SOURCE = os.getenv('DB_SCHEMA_SOURCE_DATA_SANITY')
DATA_SANITY_TBL = os.getenv('DATA_SANITY_TBL')

connection_url = f'postgresql+psycopg2://{DB_USER_SOURCE}:{DB_PASSWORD_SOURCE}@{DB_HOST_SOURCE}:{DB_PORT_SOURCE}/{DB_NAME_SOURCE}'


# for data sanity for the last run date
data_sanity_last_run_date_query = f"""
        WITH base_data AS (
                SELECT
                    month,
                    sub_domain_name as sub_domain,
                    dashboard,
                    distinct_order_count as doc,
                    distinct_order_count_till_last_run_date as doctlrd,
                    run_date, last_run_date
    
                FROM
                {DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL} where run_date = (select max(run_date) from {DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL})
            ),
            pivot_data AS (
                SELECT
                    month,
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS NO_OD_B2C,
                    
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS NO_OD_B2B,
                    
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS NO_OD_GV,
                    
                    MAX(CASE WHEN dashboard = 'NO_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS NO_OD_Logistics,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS OD_L1_B2C,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS OD_L1_B2B,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS OD_L1_GV,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS OD_L1_Logistics,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS L1_L2_B2C,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS L1_L2_B2B,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS L1_L2_GV,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L1_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS L1_L2_Logistics,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'B2C' THEN doc ELSE 0 END) AS L2_L3_B2C,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'B2B' THEN doc ELSE 0 END) AS L2_L3_B2B,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'GV' THEN doc ELSE 0 END) AS L2_L3_GV,
                    
                    MAX(CASE WHEN dashboard = 'OD_with_L2_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_L3_query' AND sub_domain = 'Logistics' THEN doc ELSE 0 END) AS L2_L3_Logistics,
                    run_date
                FROM
                    base_data
                GROUP BY
                    month, run_date
            )
            SELECT
                month,
                NO_OD_B2C AS "NO-OD B2C",
                NO_OD_B2B AS "NO-OD B2B",
                NO_OD_GV AS "NO-OD GV",
                NO_OD_Logistics AS "NO-OD Logistics",
                OD_L1_B2C AS "OD-L1 B2C",
                OD_L1_B2B AS "OD-L1 B2B",
                OD_L1_GV AS "OD-L1 GV",
                OD_L1_Logistics AS "OD-L1 Logistics",
                L1_L2_B2C AS "L1-L2 B2C",
                L1_L2_B2B AS "L1-L2 B2B",
                L1_L2_GV AS "L1-L2 GV",
                L1_L2_Logistics AS "L1-L2 Logistics",
                L2_L3_B2C AS "L2-L3 B2C",
                L2_L3_B2B AS "L2-L3 B2B",
                L2_L3_GV AS "L2-L3 GV",
                L2_L3_Logistics AS "L2-L3 Logistics",
                run_date
            FROM
                pivot_data
            ORDER BY
                month DESC;
"""
df = pd.read_sql_query(data_sanity_last_run_date_query,connection_url)
print(df)


# for athena varience OD
source_data_query = f"""
    SELECT
        month,
        sub_domain_name as sub_domain,
        dashboard,
        distinct_order_count as doc,
		distinct_order_count_till_last_run_date as doctlrd,
		run_date, last_run_date

    FROM
	{DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL} order by run_date
"""
df = pd.read_sql_query(source_data_query,connection_url)

date_pairs = df[['run_date', 'last_run_date']].drop_duplicates().values.tolist()
dataframes = []

for run_date, last_run_date in date_pairs:

    if not run_date or not last_run_date:
        continue


    athena_od_varience_query = f"""
        WITH 
            base_data AS (
                SELECT
                    month,
                    sub_domain_name as sub_domain,
                    dashboard,
                    distinct_order_count as doc,
                    distinct_order_count_till_last_run_date as doctlrd,
                    run_date, last_run_date

                FROM
                {DB_SCHEMA_SOURCE}.{DATA_SANITY_TBL} where run_date in ('{run_date}', '{last_run_date}')
            ),
            pivot_data AS (
                SELECT
                    month,
                    (MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' AND run_date = '{run_date}' THEN doctlrd ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2C' AND run_date = '{last_run_date}' THEN doc ELSE 0 END))
                    AS OD_B2C,

                    (MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' AND run_date = '{run_date}' THEN doctlrd ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'B2B' AND run_date = '{last_run_date}' THEN doc ELSE 0 END))
                    AS OD_B2B,

                    (MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Voucher' AND run_date = '{run_date}' THEN doctlrd ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Voucher' AND run_date = '{last_run_date}' THEN doc ELSE 0 END))
                    AS OD_GV,

                    (MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' AND run_date = '{run_date}' THEN doctlrd ELSE 0 END) -
                    MAX(CASE WHEN dashboard = 'OD_with_base_query' AND sub_domain = 'Logistics' AND run_date = '{last_run_date}' THEN doc ELSE 0 END))
                    AS OD_Logistics

                FROM
                    base_data
                GROUP BY
                    month
            )
            SELECT
                month,
                OD_B2C as "OD_B2C",
                OD_B2B as "OD_B2B",
                OD_GV as "OD_B2B",
                OD_Logistics as OD_Logistics,
                '{run_date} - {last_run_date}' as run_date_diff

            
            FROM
                pivot_data
            ORDER BY
                month DESC;

        """
    
    df = pd.read_sql(athena_od_varience_query, connection_url)
    
    # Append the resulting DataFrame to the list
    dataframes.append(df)

combined_df = pd.concat(dataframes, ignore_index=True)


print("ran successfully")

print(combined_df)