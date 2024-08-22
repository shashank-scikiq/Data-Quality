import sys

sys.path.append("../")

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import Logic.base_queries as bq
from decimal import Decimal


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

# Default Filter is Date and Seller NP name. Will Go Across all.
max_date = bq.get_date_range()[1]


# def_sell_np = None


def calc_metrices(df: pd.DataFrame, col_name: str):
    old_val = np.round(df[col_name][1], 4)
    new_val = np.round(df[col_name][0], 4)
    diff = new_val - old_val
    per_diff = np.round((diff / old_val) * 100, 4)
    return new_val, diff, per_diff

def serialize_decimal(value):
    """Convert Decimal to float for JSON serialization."""
    if isinstance(value, Decimal):
        return float(value)
    return value


def process_data(df):
    # Ensure all numerical columns are filled and converted properly
    for x in df.columns:
        if x not in ["ord_date", "seller_np"]:
            df[x] = df[x].fillna(0)
            df[x] = df[x].replace("", 0)
            df[x] = df[x].astype(int)
            

def top_cards_delta(start_date: datetime = max_date, seller_np: str = None):
    prev_dt = start_date - timedelta(days=1)
    df_temp = bq.query_top_cards(start_date, prev_dt, seller_np)
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


def missing_percentage(start_date: datetime = max_date, seller_np: str | None = None):
    prev_dt = start_date - timedelta(days=1)
    res = []
    df_res = bq.query_missing_percentage(start_date, prev_dt, seller_np)
    curr_total = int(df_res["total_orders"][0])
    for col in df_res.columns:
        if col.__contains__("null"):
            per = np.round((int(df_res[col][0]) / curr_total) * 100, 4)
            if per > 0:
                tmp_dict = {
                    'title': cols_dict[col],
                    'series': [np.round(float(per), 2)]
                }
                res.append(tmp_dict)
    return res


def missing_per_by_seller(count: int = 5, start_date: datetime = max_date,
                          threshold: float = 0.05, seller_np: str | None = None):
    df = bq.query_highest_missing_by_seller(start_date, count, seller_np)
    df["missing_percentage"] = df["missing_val"] / df["total_orders"]
    df = df.sort_values(by="missing_percentage", ascending=False)
    json_str = []
    for x in df.index:
        json_frame = {
            "id": df.iloc[x]["seller_np"],
            "count": str(np.round(float((df.iloc[x]["missing_percentage"]))*100, 2))+"%",
            "increased": True if df.iloc[x]["missing_percentage"] > 0 else "False",
            "variancePercentage": float(threshold * 100), "varianceText": "Threshold"}
        json_str.append(json_frame)
    return json_str


def detailed_completed_table(count: int = 15, start_date: datetime = max_date,
                             seller_np: str | None = None):
    df = bq.query_detailed_completed_table(start_date, count, seller_np)
    df = df.applymap(serialize_decimal)
    df["ord_date"] = df["ord_date"].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else x)
    data = df.to_dict(orient='records')
    # return {"title": "Detailed Missing Data Table", "data": data}
    return data


def data_sanity_last_run_date_report():
    df = bq.query_data_sanity_last_run_date_report()
    df['month'] = pd.to_datetime(df['month']).dt.strftime('%b %Y')
    df['run_date'] = pd.to_datetime(df['run_date']).dt.strftime('%Y-%m-%d')
    data = df.to_dict(orient='records')
    # print(data)
    return {"title": "Last Run Date Report", "data": data}


def ds_variance_data_report():
    df = bq.query_data_variance_report()
    # df['month'] = df['month'].str.replace(" 00:00:00", "")
    df['month'] = pd.to_datetime(df['month']).dt.strftime('%b %Y')
    data = df.to_dict(orient='records')
    return {"title": "Data Variance Report", "data": data}


def order_stats(count: int = 100,
                start_date: datetime = max_date,
                seller_np: str | None = None):
    result = bq.query_order_stats(start_date=start_date, count=count,
                                   seller_np=seller_np)
    df = pd.DataFrame(result)
    df["order_date"] = df["order_date"].apply(lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else x)
    data = df.to_dict(orient='records')
    return data
    

# def order_stats(count: int = 15,
#                 start_date: datetime = max_date,
#                 seller_np: str | None = None):
#     result = bq.query_order_stats(start_date=start_date, count=count,
#                                   seller_np=seller_np)
#     if result:
#         df = pd.DataFrame(result)
#         df["cancellation_code_missing"] = df["cancellation_code_missing"].fillna(0).astype(int)
#         df["Total_orders"] = df["in_progress"] + df["completed"] + df["cancelled"]
#         df.sort_values(by=["Total_orders", "cancelled", "cancellation_code_missing"], ascending=False)
#         json_frame = []
#         for x in df.index:
#             json_str = {
#                 "Seller NP": df.loc[x]["seller_np"],
#                 "Total Orders": int(df.loc[x]["Total_orders"]),
#                 "In Progress": int(df.loc[x]["in_progress"]),
#                 "Completed": int(df.loc[x]["in_progress"]),
#                 "Total Cancellations": int(df.loc[x]["cancelled"]),
#                 "Cancellation Code missing": int(df.loc[x]["cancellation_code_missing"])
#             }
#             json_frame.append(json_str)
#     else:
#         json_frame = [{
#             "Seller NP": "NA",
#             "Total Orders": 0,
#             "In Progress": 0,
#             "Completed": 0,
#             "Total Cancellations": 0,
#             "Cancellation Code missing": 0}
#         ]

#     return json_frame


def trend_chart(start_date: datetime | None = None):
    df = bq.query_trend_chart(start_date)
    final_json = {
        'title': 'Chart Title',
        'series': [],
        'categories': []
    }
    for col in df.columns:
        if col == 'ord_date':
            final_json['categories'] = df[col].astype(str).tolist()
        else:
            data_ser = {
                'name': cols_dict[col],
                'data': df[col].astype(int).tolist()
            }
            final_json['series'].append(data_ser)
    final_json['title'] = 'Columns with Highest Missing Data'
    return final_json
