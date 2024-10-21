import os
from dotenv import load_dotenv
import re
import sys
try:
  env_file="D:\\Work\\git\\Data-Quality\\FA_Backend\\.env"
  load_dotenv(env_file)
except Exception as e:
  raise e
else:
  print("Env loaded in utils.")

aws_region = os.getenv('AWS_REGION')
aws_secret_access_key = os.getenv('AWS_SECRET_KEY')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
ATH_DB = os.getenv('ATH_DB')
S3_LOCATION = os.getenv('S3_STAGING_DIR')
BASE_TABLE = os.getenv("nhm_order_fulfillment_subset_v1")

PG_USER = os.getenv("PG_USERNAME")
PG_PASSWD = os.getenv("PG_PASSWD")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DB = os.getenv("PG_DB")
PG_SCHEMA = os.getenv("PG_SCHEMA")

DQ_TBL = os.getenv("DQ_TABLE")
AGG_VIEW = os.getenv("AGG_VIEW")
AGG_SUM = os.getenv("AGG_SUM")
COL_SUM = os.getenv("COL_SUM")
DIM_ORD_STAT = os.getenv("DIM_ORD_STAT")
DIM_SELLERS = os.getenv("DIM_SELLERS")
AGG_ORD_STATS = os.getenv("AGG_ORD_STATS")
DS_TABLE = os.getenv("DS_TABLE")
DS_LAST_RUN_DATE = os.getenv("DS_LAST_RUN_DATE")

print(aws_region)

def check_env_vars():
  pass


def read_file(f_name: str) -> list[str]:
  """
  f_name = The file name which needs to be read along with
  the location.

  Returns a list of contents.
  """
  file_contents: list[str] = []
  if os.path.exists(f_name):
    toolkit_logger.info(f"Found File {f_name}.")
    try:
      with open(f_name, 'r') as f:
        file_contents = f.readlines()
    except Exception as e:
      toolkit_logger.info(e.args[0])
      sys.exit()
    else:
      print("File read successfully.")
  else:
    print("File {} not Found. Exiting. ".format(f_name))
    sys.exit()
  return file_contents


def read_clean_script(f_name: str, env_file: str) -> str:
  """
  f_name = The file name which needs to be read. This will be a
  sql script that will be read by this function. It will replace
  any environment file reference with its value.

  env_file = File containing the environment variables.
  """

  incl_kws = ["POSTGRES_DB", "_SCHEMA", "ATH", "TBL", "VER_", "START"]
  all_envs = read_file(env_file)
  repl_dict = {key.split('\n')[0]: os.getenv(key.split('\n')[0]) for key in all_envs if
               any(kw in key for kw in incl_kws)}
  # print(repl_dict)

  to_run = read_file(f_name)
  val = "".join(to_run)
  # print(val)

  for key, value in repl_dict.items():
    try:
      val = re.sub(rf'\b{re.escape(key)}\b', value, val)
    except Exception as e:
      toolkit_logger.error("Error while replacing the values.")
      print(key, value)
      print(str(e))
      sys.exit()
  return val