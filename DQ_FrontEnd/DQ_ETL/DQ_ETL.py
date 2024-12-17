import os

from FA_Backend.Models.models import od_dq_base
from Extract_data import extractData
from Load_data import dqLoadDb
import asyncio


def etlMain():
    print(od_dq_base.name)
    files_loc = os.getenv("DQ_DUMP_LOC")
    asyncio.run(dqLoadDb(files_loc))

if __name__ == "__main__":
    asyncio.run(extractData())