import os
import utils

import pandas as pd
import sqlalchemy as sa
from datetime import datetime, timedelta
from glob import glob
from EXT_ATH import process_date
from dotenv import load_dotenv


user = utils.PG_USER
if not user:
	print("Environment not loaded.")
else:
	print("Environment variables are loaded.")

