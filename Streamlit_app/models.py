import pandas as pd
import streamlit as st
from get_data import od_dq, run_stmt
from sqlalchemy import Select, func, extract
from datetime import date, datetime


@st.cache_data
def get_date_range():
    date_range = (
        Select(func.min(od_dq.c.ord_date), func.max(od_dq.c.ord_date))
    )
    dt_rng = run_stmt(date_range)[0]
    return dt_rng[0], dt_rng[1]


min_ord_date = get_date_range()[0]
max_ord_date = get_date_range()[1]


@st.cache_data
def load_cancelled_orders(dt_val: date, total=0):
    cancelled = (
        Select(od_dq.c.ord_date, od_dq.c.seller_np,
               func.sum(od_dq.c.null_cans_code).label("Cancellation_code"),
               func.sum(od_dq.c.null_cans_dt_time).label("Cancelled_Dates"))
        .where(od_dq.c.total_canceled_orders > 0)
        .where(od_dq.c.null_cans_code > 0)
        .where(od_dq.c.ord_date == dt_val)
        .group_by(od_dq.c.ord_date, od_dq.c.seller_np)
    )
    return run_stmt(cancelled, total)


@st.cache_data
def load_missing_pc(dt_val: str, col_name: str, total=0) -> list[str]:
    col_ = getattr(od_dq.c, col_name)
    missing_col = (
        Select(
            od_dq.c.seller_np,
            col_,
            od_dq.c.total_orders)
        .where(col_ > 0)
        .where(od_dq.c.ord_date == dt_val)
        .order_by(col_.desc())
    )
    return run_stmt(missing_col, total)


@st.cache_data
def curr_date() -> str:
    curr_dt = (
        Select(func.max(od_dq.c.curr_date))
    )
    return run_stmt(curr_dt)


@st.cache_data
def get_columns() -> list[str]:
    return od_dq.columns.keys()


@st.cache_data
def get_sellers(dt_val: str) -> list[str]:
    sellers = (
        Select(
            od_dq.c.seller_np).distinct().where(
            od_dq.c.ord_date == dt_val)
    )
    return run_stmt(sellers)


@st.cache_data
def get_per_col(dt_val: str) -> list[pd.DataFrame]:
    all_data = (
        Select(od_dq)
        .where(od_dq.c.ord_date == dt_val)
    )
    df = pd.DataFrame(run_stmt(all_data))
    # print(df)
    null_cols = [x for x in df.columns if x.__contains__('null') and not x.__contains__('cans')]
    null_cols.append("total_orders")
    null_cols_canc = [x for x in df.columns if x.__contains__('null') and x.__contains__('cans')]
    null_cols_canc.append("total_canceled_orders")
    df_completed = df[null_cols]
    df_canc = df[null_cols_canc]
    return df_completed, df_canc


@st.cache_data
def get_all_df(dt_val: str, total=0) -> pd.DataFrame:
    # parsed_date = datetime.strptime(dt_val, "%Y-%m-%d")
    all_curr_mnth = (
        Select(od_dq)
        .where(extract("month", od_dq.c.ord_date) == dt_val.month)
    )
    return pd.DataFrame(run_stmt(all_curr_mnth, total))


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
