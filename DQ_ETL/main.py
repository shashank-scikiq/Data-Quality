import os
import sys
import pathlib

current_path = pathlib.Path(__file__).resolve()
project_root = current_path.parent.parent
sys.path.append(str(project_root))

from .backend.models import od_dq_base
from .extractData.Extract_data import dataDump
from .loadData.Load_data import dqLoadDb
import asyncio


def etlMain():
	print(od_dq_base.name)
	files_loc = os.getenv("DQ_DUMP_LOC")
	asyncio.run(dqLoadDb(files_loc))

if __name__ == "__main__":
	asyncio.run(dataDump())