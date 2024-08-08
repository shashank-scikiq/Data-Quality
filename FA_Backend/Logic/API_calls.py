import pandas as pd
from datetime import datetime, timedelta
import numpy as np

import sys
sys.path.append("../")

import Logic.base_queries as bq
import Misc.env_vars as ev

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


def calc_metrices(df: pd.DataFrame, col_name: str):
    old_val = np.round(df[col_name][1], 4)
    new_val = np.round(df[col_name][0], 4)
    diff = new_val - old_val
    per_diff = np.round((diff / old_val) * 100, 4)
    return new_val, diff, per_diff


def top_cards_delta(start_date: datetime.date = None) -> str:
    if not start_date:
        start_date = bq.get_date_range()[1]
    prev_dt = start_date - timedelta(days=1)
    print(start_date, prev_dt)
    df_temp = bq.query_top_cards(start_date, prev_dt)
    print(df_temp)
    df_temp.loc[:, "Total_Orders"] = df_temp["Total_Orders"].astype(int)
    df_temp.loc[:, "Cancelled_Orders"] = df_temp["Cancelled_Orders"].astype(int)
    df_temp["Cancel_percentage"] = df_temp["Cancelled_Orders"] / df_temp["Total_Orders"]
    df_temp["Completed_percentage"] = (df_temp["Total_Orders"] - df_temp["Cancelled_Orders"]) / df_temp["Total_Orders"]
    tt, td, tp = calc_metrices(df_temp, "Total_Orders")
    tc, cd, cp = calc_metrices(df_temp, "Cancelled_Orders")
    cct, ccd, ccp = calc_metrices(df_temp, "Cancel_percentage")
    cot, cod, cop = calc_metrices(df_temp, "Completed_percentage")
    total_orders = {
        "title": "Total Orders",
        "count": str(tt),
        "increased": False if td < 0 else True,
        "variancePercentage": str(tp),
        "varianceText": "vs Yesterday"
    }
    total_cancellation = {
        "title": "Cancelled Orders",
        "count": str(tc),
        "increased": False if cd < 0 else True,
        "variancePercentage": str(cp),
        "varianceText": "vs Yesterday"
    }
    cancel_percentage = {
        "title": "Order Cancellation %",
        "count": str(cct),
        "increased": False if ccd < 0 else True,
        "variancePercentage": str(ccp),
        "varianceText": "vs Yesterday"
    }
    compl_percentage = {
        "title": "Order Completion %",
        "count": str(cot),
        "increased": False if cod < 0 else True,
        "variancePercentage": str(cop),
        "varianceText": "vs Yesterday"
    }
    final_list = [total_orders, total_cancellation, cancel_percentage, compl_percentage]
    return final_list


def missing_percentage(start_date: datetime.date = None) -> str:
    if not start_date:
        start_date = bq.get_date_range()[1]
    prev_dt = start_date - timedelta(days=1)
    res = []
    tmp_dict = {}

    df_res = bq.query_missing_percentage(start_date, prev_dt)
    curr_total = int(df_res["total_orders"][0])
    for col in df_res.columns:
        if col.__contains__("null"):
            per = np.round((int(df_res[col][0])/curr_total)*100,4)
            if per > 0:
                tmp_dict = {}
                tmp_dict['title'] = cols_dict[col]
                tmp_dict['series'] = [float(per)]
                res.append(tmp_dict)
    
    return res


def missing_seller_np(count: int, start_date: datetime.date = None) -> str:
    if not start_date:
        start_date = bq.get_date_range()[1]
    df = bq.query_highest_missing_by_seller(start_date, count)
    