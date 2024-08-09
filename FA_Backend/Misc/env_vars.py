from dotenv import load_dotenv
import os
import sys


try:
    ENV_FILE = os.getenv(".env")
    load_dotenv(ENV_FILE)
except Exception as e:
    raise e
else:
    print("Loaded Env from File.")
    

# Other Variables. 
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_USER = os.getenv("PG_USERNAME")
PG_PWD = os.getenv("PG_PASSWD")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")
DQ_TBL = os.getenv("DQ_TABLE")
AGG_VIEW = os.getenv("AGG_VIEW")
AGG_SUM = os.getenv("AGG_SUM")
COL_SUM = os.getenv("COl_SUM")

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

def chk_env_vars():
    required_vars = ["PG_HOST", "PG_PORT",
                    "PG_USERNAME", "PG_PASSWD", "PG_DB",
                    "PG_SCHEMA", "DQ_TABLE", "AGG_VIEW","AGG_SUM",
                    "COL_SUM"]
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

chk_env_vars()