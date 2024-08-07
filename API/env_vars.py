from dotenv import load_dotenv
import os
import sys


try:
    ENV_FILE = os.getenv(".env")
    load_dotenv(ENV_FILE)
except Exception as e:
    raise e
else:
    print("Environment variables loaded successfully.")
    

# Other Variables. 
db_host = os.getenv("POSTGRES_HOST")
db_port = os.getenv("POSTGRES_PORT")
db_user = os.getenv("POSTGRES_USER")
db_pwd = os.getenv("POSTGRES_PASSWORD")
db_instance = os.getenv("POSTGRES_DB")
db_schema = os.getenv("POSTGRES_SCHEMA")
dq_table = os.getenv("OD_DQ_TBL")
agg_view = os.getenv("DQ_AGG_VIEW")
agg_sum = os.getenv("DQ_AGG_SUM")

cols_dict = {
    "curr_date": "Current Date",
    "ord_date": "Order Date",
    "seller_np": "Seller NP",
    "null_fulfilment_id": "Fulfilment ID",
    "null_net_tran_id": "Net Transaction ID",
    "null_qty": "Quantity",
    "null_itm_fulfilment_id": "Item Fulfilment ID",
    "null_del_pc": "Delivery Pincode",
    "null_created_date_time": "Created Date",
    "null_domain": "Domain",
    "null_del_cty": "Delivery City",
    "null_cans_code": "Cancellation Code",
    "null_cans_dt_time": "Cancellation Date",
    "null_ord_stats": "Order Status",
    "null_fulfil_status": "Fulfilment Status",
    "null_itm_cat": "Item Category",
    "null_cat_cons": "Category",
    "null_sell_pincode": "Seller Pincode",
    "null_prov_id": "Provider ID",
    "null_itm_id": "Item ID",
    "null_sell_np": "Null Seller NP",
    "null_net_ord_id": "Network Order ID",
    "null_sell_cty": "Seller City"
}

#  Check Required Environment Variables.  

required_vars = ["POSTGRES_HOST", "POSTGRES_PORT",
				"POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB",
				"POSTGRES_SCHEMA", "OD_DQ_TBL", "DQ_AGG_SUM","DQ_AGG_VIEW"]
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