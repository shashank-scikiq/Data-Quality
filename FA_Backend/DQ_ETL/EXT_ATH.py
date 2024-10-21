import sys
import aioboto3
import asyncio

import utils
from utils import aws_region,aws_secret_access_key,aws_access_key_id
from utils import ATH_DB, S3_LOCATION, env_file
from botocore.exceptions import ClientError


async def execute_athena_query(tbl_name:str, date_val:str, query:str, semaphore: asyncio.Semaphore, max_retries:int = 5):
	"""
	Execute a formatted query on AWS Athena. Following are the parameters it accepts.
	table_name: The name of raw table.
	date_val : The date value for which this query is executed. This is just for logging purpose.
	query: The formatted, final query that needs to be executed.

	"""
	if not aws_access_key_id or not aws_secret_access_key:
		raise Exception("AWS credentials are not set in environment variables.")
	else:
		print("AWS Credentials Found.")
		# print(aws_region)
	async with semaphore:
		async with aioboto3.Session().client('athena', region_name=aws_region,
											 aws_access_key_id=aws_access_key_id,
											 aws_secret_access_key=aws_secret_access_key) as client:
			retries = 0
			while retries < max_retries:
				try:
					response = await client.start_query_execution(
						QueryString=query,
						QueryExecutionContext={'Database': ATH_DB},
						ResultConfiguration={'OutputLocation': S3_LOCATION}
					)
					query_execution_id = response['QueryExecutionId']

					print(f"Executing query for : {tbl_name}:{date_val}")
					status = 'RUNNING'
					while status in ('RUNNING', 'QUEUED'):
						response = await client.get_query_execution(QueryExecutionId=query_execution_id)
						status = response['QueryExecution']['Status']['State']

						if status in ('FAILED', 'CANCELLED'):
							state_change_reason = response['QueryExecution']['Status'].get('StateChangeReason',
																						   'No reason provided')
							print(
								f"Query failed for {tbl_name}:{date_val} with status: {status}. Reason: {state_change_reason}")
							raise Exception(f"Query failed with status: {status}. Reason: {state_change_reason}")
						await asyncio.sleep(2)

					results = []
					next_token = None
					column_info = None

					while True:
						if next_token:
							response = await client.get_query_results(QueryExecutionId=query_execution_id,
																	  NextToken=next_token)
						else:
							response = await client.get_query_results(QueryExecutionId=query_execution_id)

						if not column_info:
							column_info = response['ResultSet']['ResultSetMetadata']['ColumnInfo']

						results.extend(response['ResultSet']['Rows'])
						next_token = response.get('NextToken')
						if not next_token:
							break

					return {'column_info': column_info, 'rows': results}

				except ClientError as e:
					if e.response['Error']['Code'] == 'TooManyRequestsException':
						retries += 1
						wait_time = min(2 ** retries, 60)
						print(
							f"TooManyRequestsException encountered for {tbl_name}:{date_val}. Retrying in {wait_time} seconds...")
						await asyncio.sleep(wait_time)
					else:
						print(f"ClientError encountered for {tbl_name}:{date_val}. Error: {e}")
						raise e


async def process_date(tbl_name:str, date:str, raw_query: str, semaphore=asyncio.Semaphore(5)):
	"""
	This query will extract data for a specific date.
	tbl_name = Name of the raw table.
	date_val = Date in YYYY-MM-DD format.
	raw_query = The raw query to be processed.
	"""

	formatted_query = raw_query.format(date_val = date)
	try:
		result = await execute_athena_query(tbl_name, date, formatted_query, semaphore)
	except Exception as e:
		raise e
	else:
		return result


async def process_agg_date(tbl_name: str, agg_type: str, agg_val: str,
						   raw_query: str, semaphore=asyncio.Semaphore(5)):
	"""
	This query will extract data at an aggregated date period. The aggregations could be month, year and week.
	tbl_name = Name of the raw table.
	date_agg_type = Date aggregation types.
	date_agg_val = Date aggregation value.
	raw_query = The raw query to be processed.
	"""

	formatted_query = raw_query.format(date_agg_type = agg_type, date_agg_val = agg_val)

	try:
		result = await execute_athena_query(tbl_name, agg_val, formatted_query, semaphore)
	except Exception as e:
		raise e
	else:
		return result