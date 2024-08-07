import pandas as pd
import os
from datetime import date, datetime

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import Select, func, extract
# import asyncpg 

import env_vars as ev
import models as mdl
from models import od_dq_base


async_engine = create_async_engine(f"postgresql+asyncpg://{ev.db_user}:{ev.db_pwd}@{ev.db_host}:{ev.db_port}/{ev.db_instance}")

async def check_envs(env_vars):
	for var in env_vars:
		if var not in os.environ:
			raise KeyError(f"Environment variable '{var}' is not loaded.")


async def run_stmt(to_run, cnt=0):
    stmt = (to_run)
    async with async_engine.connect() as conn:
        if cnt > 0:
            try:
                result = await conn.execute(stmt)
                return result.fetchmany(cnt)
            except Exception as e:
                raise e
        else:
            try:
                result = await conn.execute(stmt)
                return result.fetchall()
            except Exception as e:
                raise e


async def get_date_range():
    date_range = (
        Select(func.min(od_dq_base.c.ord_date), func.max(od_dq_base.c.ord_date))
    )
    dt_rng = await run_stmt(date_range)
    return dt_rng


# min_ord_date = get_date_range()[0]
# max_ord_date = get_date_range()[1]

# async def 