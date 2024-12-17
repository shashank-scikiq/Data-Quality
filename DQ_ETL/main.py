import os
import sys
import pathlib

current_path = pathlib.Path(__file__).resolve()
project_root = current_path.parent.parent
sys.path.append(str(project_root))

from backend.models import od_dq_base
from extractData.Extract_data import dataDump
from loadData.Load_data import dqLoadDb
import asyncio


async def etlMain():
	print(od_dq_base.name)
	print("Extracting the Data from AWS Athena.")

	try:
		files_loc = await dataDump()
	except Exception as e:
		raise e
	else:
		print("Data Extracted successfully.")

	print("Loading the Data into Postgresql.")
	try:
		await dqLoadDb(files_loc)
	except Exception as e:
		raise e
	else:
		print("Data Extracted successfully.")

	print('ETL Process completed successfully.')


if __name__ == "__main__":
	asyncio.run(etlMain())