import os
from datetime import datetime
import re

dt_today = str(datetime.today().date())


def check_last_folder(folder_path: str):
	for fold, _, _ in os.walk(folder_path):
		curr_dir = fold
		regex = r"(\d+-\d+-\d+)"
		try:
			date_val = re.findall(regex, curr_dir)
			last_upd_month = datetime.strptime(date_val[0], "%Y-%m-%d").month
			curr_mnth = datetime.now().month
			if last_upd_month == curr_mnth:
				print(f"Data Exists. Setting the dump loc to {curr_dir} ")
				return curr_dir
		except:
			continue
	else:
		tgt_fold = f"{folder_path}/DATA_QUALITY-{str(dt_today)}"
		print(f"Setting the dump loc to {tgt_fold} ")
		return tgt_fold


def check_create_folders(data_loc: str):
	base_loc = None
	raw_files = None
	processed_files = None
	total_orders = None
	logistic_search = None
	if os.path.exists("/app/DB_Scripts/"):
		base_loc = check_last_folder(data_loc)
		raw_files = f"{base_loc}/DQ_RAW_FILES/"
	elif os.path.exists(os.getenv('DQ_DUMP_LOC')):
		# If the script is run from outside docker but the folders exists.
		base_loc = check_last_folder(data_loc)
		print(base_loc)
		raw_files = f"{base_loc}/DQ_RAW_FILES/"
	dirs_to_check = [raw_files]

	for dir_name in dirs_to_check:
		if os.path.exists(dir_name):
			print(f"{dir_name} already exists for processing.")
		else:
			print("Creating folder.")
			print(dir_name)
			try:
				os.mkdir(dir_name)
			except Exception as e:
				raise e
	else:
		print("Folder operation successful.")
		return dirs_to_check

# if __name__ == "__main__":
#     check_folder()