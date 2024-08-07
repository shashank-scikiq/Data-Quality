import pandas as pd

from typing import Tuple, Any
from sqlalchemy import Select, func, extract
from datetime import date
import os
import sys

sys.path.insert(0,  "../Models")

from Models.models import engine
from Models.models import od_dq_base


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
