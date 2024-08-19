import pandas as pd

from typing import Tuple, Any
from sqlalchemy import Select, func, and_, or_, desc
from datetime import date, datetime
import os
import sys

from sqlalchemy import create_engine

sys.path.insert(0, "../Models")

from Models.models import engine
from Models.models import (od_dq_base, dq_agg_view, dq_agg_sum, dq_col_sum,
                           dq_dim_order_status, dq_dim_sellers, ds_data_sanity, dq_agg_order_stats,
                           ds_last_run_date)
from Misc import env_vars as ev


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


def get_date_range():
    date_range = (
        Select(func.min(od_dq_base.c.ord_date), func.max(od_dq_base.c.ord_date))
    )
    dt_rng = run_stmt(date_range)[0]
    return dt_rng[0], dt_rng[1]


def get_sellers_by_date(date_val):
    sellers = Select(dq_dim_sellers).where(dq_dim_sellers.c.order_date == date_val)
    df = pd.DataFrame(run_stmt(sellers))
    sellers_list = list(df["seller_np"])
    del df
    return sellers_list


def curr_date() -> str:
    curr_dt = (
        Select(func.max(od_dq_base.c.curr_date))
    )
    return run_stmt(curr_dt)


def get_columns() -> list[str]:
    return od_dq_base.columns.keys()


def query_top_cards(curr_dt: datetime, prev_dt: datetime, seller_np: str) -> pd.DataFrame:
    top_cards = (
        (Select(
            dq_agg_sum.c.ord_date.label("Order_Date"),
            func.sum(dq_agg_sum.c.total_orders).label("Total_Orders"),
            func.sum(dq_agg_sum.c.total_canceled_orders).label("Cancelled_Orders")
        ).where(and_(
            (or_(dq_agg_sum.c.ord_date == curr_dt, dq_agg_sum.c.ord_date == prev_dt)),
            dq_agg_sum.c.seller_np == seller_np if seller_np else True))
         .group_by(dq_agg_sum.c.ord_date)
         .order_by(desc(dq_agg_sum.c.ord_date))
         )
    )
    result = run_stmt(top_cards)
    return pd.DataFrame(result)


def query_missing_percentage(curr_dt: datetime, prev_dt: datetime, seller_np: str) -> pd.DataFrame:
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
        ).where(and_(
            or_(dq_agg_view.c.ord_date == curr_dt, dq_agg_view.c.ord_date == prev_dt),
            dq_agg_view.c.seller_np == seller_np if seller_np else True))
        .group_by(dq_agg_view.c.ord_date)
        .order_by(desc(dq_agg_view.c.ord_date))
    )
    result = run_stmt(col_sum_comp)
    return pd.DataFrame(result)


def query_canc_percentage(curr_dt: datetime, prev_dt: datetime, seller_np: str) -> pd.DataFrame:
    col_sum_canc = (
        Select(
            dq_agg_view.c.ord_date,
            func.sum(dq_agg_view.c.total_canceled_orders).label("total_canceled_orders"),
            func.sum(dq_agg_view.c.null_cans_code).label("null_cans_code"),
            func.sum(dq_agg_view.c.null_cans_dt_time).label("null_cans_dt_time")
        ).where(and_(
            or_(dq_agg_view.c.ord_date == curr_dt, dq_agg_view.c.ord_date == prev_dt),
            dq_agg_view.c.seller_np == seller_np if seller_np else True))
        .group_by(dq_agg_view.c.ord_date)
        .order_by(desc(dq_agg_view.c.ord_date))
    )
    result = run_stmt(col_sum_canc)
    return pd.DataFrame(result)


def query_highest_missing_by_seller(curr_dt: datetime, count: int, seller_np: str) -> pd.DataFrame:
    stmt_curr = (Select(
        dq_agg_sum.c.ord_date,
        dq_agg_sum.c.seller_np,
        func.sum(dq_agg_sum.c.total_orders).label("total_orders"),
        func.sum(dq_agg_sum.c.sum_missing_cols).label("missing_val")).
                 where(and_(dq_agg_sum.c.ord_date == curr_dt,
                            dq_agg_sum.c.seller_np == seller_np if seller_np else True)).
                 group_by(dq_agg_sum.c.ord_date).
                 group_by(dq_agg_sum.c.seller_np).
                 order_by(desc(func.sum(dq_agg_sum.c.sum_missing_cols))))
    result = run_stmt(stmt_curr, count)
    return pd.DataFrame(result)


def query_detailed_completed_table(curr_dt: datetime, count: int, seller_np: str) -> pd.DataFrame:
    stmt = (Select(
        dq_agg_sum.c.seller_np,
        func.sum(dq_agg_sum.c.total_orders).label("total_orders"),
        func.sum(dq_agg_sum.c.sum_missing_cols).label("sum_missing_cols")).
            where(and_(dq_agg_sum.c.ord_date == curr_dt,
                       dq_agg_sum.c.seller_np == seller_np if seller_np else True)).
            group_by(dq_agg_sum.c.seller_np).
            order_by(desc(func.sum(dq_agg_sum.c.sum_missing_cols))))
    result = run_stmt(stmt, count)
    return pd.DataFrame(result)


def query_order_stats(start_date: datetime, count: int, seller_np: str):
    stmt = Select(dq_agg_order_stats).where(and_(
        dq_agg_order_stats.c.order_date == start_date,
        dq_agg_order_stats.c.seller_np == seller_np if seller_np else True)
    )
    result = run_stmt(stmt, count)
    if result:
        return result
    else:
        return


def query_trend_chart(start_date: datetime) -> pd.DataFrame:
    stmt = Select(dq_col_sum.c.ord_date,
                  func.sum(dq_col_sum.c.null_del_cty).label("null_del_cty"),
                  func.sum(dq_col_sum.c.null_itm_cat).label("null_itm_cat"),
                  func.sum(dq_col_sum.c.null_cat_cons).label("null_cat_cons"),
                  func.sum(dq_col_sum.c.null_cans_code).label("null_cans_code"),
                  func.sum(dq_col_sum.c.null_cans_dt_time).label("null_cans_dt_time")
                  ).group_by(dq_col_sum.c.ord_date)
    result = run_stmt(stmt)
    return pd.DataFrame(result)


def query_data_sanity_last_run_date_report() -> pd.DataFrame:
    stmt = Select(ds_last_run_date).where(
        ds_last_run_date.c.month > datetime.strptime(ev.DS_START_DATE, "%Y-%m-%d"))
    result = run_stmt(stmt)
    df = pd.DataFrame(result)
    return df


def query_data_variance_report() -> pd.DataFrame:
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
        {ev.PG_SCHEMA}.{ev.DS_TABLE} where month >= '{ev.DS_START_DATE}' order by run_date
    """
    df = pd.read_sql_query(source_data_query, engine)

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
                    {ev.PG_SCHEMA}.{ev.DS_TABLE}  where run_date in ('{run_date}', '{last_run_date}')
                    and month >= '{ev.DS_START_DATE}'
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
                    OD_GV as "OD_GV",
                    OD_Logistics as OD_Logistics,
                    '{run_date} - {last_run_date}' as run_date_diff
                FROM
                    pivot_data
                ORDER BY
                    month DESC;
            """
        df = pd.read_sql(athena_od_varience_query, engine)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


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
