import pandas as pd

from typing import Tuple, Any
from sqlalchemy import Select, func, extract, or_, desc
from datetime import date, datetime
import os
import sys

sys.path.insert(0, "../Models")

from Models.models import engine
from Models.models import od_dq_base, dq_agg_view, dq_agg_sum,dq_col_sum


def check_envs(env_vars):
    for var in env_vars:
        if var not in os.environ:
            raise KeyError(f"Environment variable '{var}' is not loaded.")


def run_stmt(to_run, cnt=0):
    stmt = (
        to_run
    )
    with engine.connect() as conn:
        if cnt > 0:
            result = conn.execute(stmt).fetchmany(cnt)
        else:
            result = conn.execute(stmt).fetchall()
    return result


if __name__ == "__main__":
    required_env_vars = ["PG_USER", "PG_PWD",
                         "PG_HOST", "PG_PORT", "PG_DB",
                         "PG_SCHEMA", "DQ_TBL", "AGG_VIEW", "AGG_SUM"]
    try:
        check_envs(required_env_vars)
        print("All required environment variables are loaded.")
    except KeyError as e:
        print(f"Error: {e}")

    engine.dispose()


def get_date_range():
    date_range = (
        Select(func.min(od_dq_base.c.ord_date), func.max(od_dq_base.c.ord_date))
    )
    dt_rng = run_stmt(date_range)[0]
    return dt_rng[0], dt_rng[1]


def load_cancelled_orders(dt_val: date, total=0):
    cancelled = (
        Select(od_dq_base.c.ord_date, od_dq_base.c.seller_np,
               func.sum(od_dq_base.c.null_cans_code).label("Cancellation_code"),
               func.sum(od_dq_base.c.null_cans_dt_time).label("Cancelled_Dates"))
        .where(od_dq_base.c.total_canceled_orders > 0)
        .where(od_dq_base.c.null_cans_code > 0)
        .where(od_dq_base.c.ord_date == dt_val)
        .group_by(od_dq_base.c.ord_date, od_dq_base.c.seller_np)
    )
    return run_stmt(cancelled, total)


def load_missing_pc(dt_val: str, col_name: str, total=0, delta=False) -> list[str]:
    # if delta
    col_ = getattr(od_dq_base.c, col_name)
    missing_col = (
        Select(
            od_dq_base.c.seller_np,
            col_,
            od_dq_base.c.total_orders)
        .where(col_ > 0)
        .where(od_dq_base.c.ord_date == dt_val)
        .order_by(col_.desc())
    )
    return run_stmt(missing_col, total)


def curr_date() -> str:
    curr_dt = (
        Select(func.max(od_dq_base.c.curr_date))
    )
    return run_stmt(curr_dt)


def get_columns() -> list[str]:
    return od_dq_base.columns.keys()


def get_sellers(dt_val: str) -> list[str]:
    sellers = (
        Select(
            od_dq_base.c.seller_np).distinct().where(
            od_dq_base.c.ord_date == dt_val)
    )
    return run_stmt(sellers)


def get_per_col(dt_val: str) -> tuple[Any, Any]:
    all_data = (
        Select(od_dq_base)
        .where(od_dq_base.c.ord_date == dt_val)
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


def get_all_df(dt_val: str, total=0) -> pd.DataFrame:
    # parsed_date = datetime.strptime(dt_val, "%Y-%m-%d")
    all_curr_mnth = (
        Select(od_dq_base)
        .where(extract("month", od_dq_base.c.ord_date) == dt_val.month)
    )
    return pd.DataFrame(run_stmt(all_curr_mnth, total))


def query_top_cards(curr_dt: datetime.date, prev_dt: datetime.date) -> pd.DataFrame:
    top_cards = (
        Select(
            dq_agg_sum.c.ord_date.label("Order_Date"),
            func.sum(dq_agg_sum.c.total_orders).label("Total_Orders"),
            func.sum(dq_agg_sum.c.total_canceled_orders).label("Cancelled_Orders")
        ).where(or_(dq_agg_sum.c.ord_date == curr_dt, dq_agg_sum.c.ord_date == prev_dt))
        .group_by(dq_agg_sum.c.ord_date)
        .order_by(desc(dq_agg_sum.c.ord_date))
    )
    result = run_stmt(top_cards)
    return pd.DataFrame(result)


def query_missing_percentage(curr_dt: datetime.date, prev_dt: datetime.date) -> pd.DataFrame:
    col_sum_comp = (
    Select(
        dq_agg_view.c.ord_date, 
        func.sum(dq_agg_view.c.total_orders).label("total_orders"),
        func.sum(dq_agg_view.c.null_fulfilment_id).label("null_fulfilment_id"),
        func.sum(dq_agg_view.c.null_net_tran_id).label("null_net_tran_id"),
        func.sum(dq_agg_view.c.null_qty.label("null_qty")),
        func.sum(dq_agg_view.c.null_itm_fulfilment_id).label("null_itm_fulfilment_id"),
        func.sum(dq_agg_view.c.null_del_pc).label("null_del_pc"),
        func.sum(dq_agg_view.c.null_created_date_time).label("null_created_date_time"),
        func.sum(dq_agg_view.c.null_domain).label("null_domain"),
        func.sum(dq_agg_view.c.null_del_cty).label("null_del_cty"),
        func.sum(dq_agg_view.c.null_ord_stats).label("null_ord_stats"),
        func.sum(dq_agg_view.c.null_fulfil_status).label("null_fulfil_status"),
        func.sum(dq_agg_view.c.null_itm_cat).label("null_itm_cat"),
        func.sum(dq_agg_view.c.null_cat_cons).label("null_cat_cons"),
        func.sum(dq_agg_view.c.null_sell_pincode).label("null_sell_pincode"),
        func.sum(dq_agg_view.c.null_prov_id).label("null_prov_id"),
        func.sum(dq_agg_view.c.null_itm_id).label("null_itm_id"),
        func.sum(dq_agg_view.c.null_sell_np).label("null_sell_np"),
        func.sum(dq_agg_view.c.null_net_ord_id).label("null_net_ord_id"),
        func.sum(dq_agg_view.c.null_sell_cty).label("null_sell_cty"),
        ).where(or_(dq_agg_view.c.ord_date==curr_dt, dq_agg_view.c.ord_date==prev_dt))
        .group_by(dq_agg_view.c.ord_date)
        .order_by(desc(dq_agg_view.c.ord_date))
    )
    result = run_stmt(col_sum_comp)
    return pd.DataFrame(result)


def query_canc_percentage(curr_dt: datetime.date, prev_dt: datetime.date) -> pd.DataFrame:
    col_sum_canc = (
    Select(
        dq_agg_view.c.ord_date, 
        func.sum(dq_agg_view.c.total_canceled_orders).label("total_canceled_orders"),
        func.sum(dq_agg_view.c.null_cans_code).label("null_cans_code"),
        func.sum(dq_agg_view.c.null_cans_dt_time).label("null_cans_dt_time")
        ).where(or_(dq_agg_view.c.ord_date==curr_dt, dq_agg_view.c.ord_date==prev_dt))
        .group_by(dq_agg_view.c.ord_date)
        .order_by(desc(dq_agg_view.c.ord_date))
    )
    result = run_stmt(col_sum_canc)
    return pd.DataFrame(result)


def query_highest_missing_by_seller(curr_dt: datetime.date, count:int) -> pd.DataFrame:
    stmt_curr = Select(
        dq_agg_sum.c.ord_date,
        dq_agg_sum.c.seller_np,
        func.sum(dq_agg_sum.c.total_orders).label("total_orders"),
        func.sum(dq_agg_sum.c.sum_missing_cols).label("missing_val")).where(
        dq_agg_sum.c.ord_date==curr_dt).group_by(
        dq_agg_sum.c.ord_date).group_by(
        dq_agg_sum.c.seller_np).order_by(desc(func.sum(dq_agg_sum.c.sum_missing_cols)))
    result = run_stmt(stmt_curr, count)
    return pd.DataFrame(result)


def query_detailed_completed_table(curr_dt: datetime.date, count:int) -> pd.DataFrame:
    stmt = Select(
        dq_agg_sum.c.seller_np,
        func.sum(dq_agg_sum.c.total_orders).label("total_orders"),
        func.sum(dq_agg_sum.c.sum_missing_cols).label("sum_missing_cols")
        ).where(dq_agg_sum.c.ord_date==curr_dt).group_by(
            dq_agg_sum.c.seller_np).order_by(desc(func.sum(dq_agg_sum.c.sum_missing_cols)))
    result = run_stmt(stmt, count)
    return pd.DataFrame(result)


def query_detailed_cancelled_table(curr_dt: datetime.date, count:int) -> pd.DataFrame:
    stmt = Select(
    dq_agg_sum.c.seller_np,
    func.sum(dq_agg_sum.c.total_canceled_orders).label("total_orders"),
    func.sum(dq_agg_sum.c.canc_metrices).label("sum_missing_cols")
    ).where(dq_agg_sum.c.ord_date==curr_dt).group_by(
        dq_agg_sum.c.seller_np).order_by(desc(
        func.sum(dq_agg_sum.c.total_canceled_orders)))
    result = run_stmt(stmt, count)
    return pd.DataFrame(result)


def query_trend_chart1() -> pd.DataFrame:
    stmt = Select(dq_col_sum.c.ord_date,
       func.sum(dq_col_sum.c.null_del_cty).label("null_del_cty"),
       func.sum(dq_col_sum.c.null_itm_cat).label("null_itm_cat"),
       func.sum(dq_col_sum.c.null_cat_cons).label("null_cat_cons"),
       func.sum(dq_col_sum.c.null_cans_code).label("null_cans_code"),
       func.sum(dq_col_sum.c.null_cans_dt_time).label("null_cans_dt_time")
       ).group_by(dq_col_sum.c.ord_date)
    result = run_stmt(stmt)
    return pd.DataFrame(result)

