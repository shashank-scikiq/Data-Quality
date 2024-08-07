import API.base_queries as mdl
import numpy as np
from dataclasses import dataclass
import pandas as pd

#  Dashboard Elements
# ====================================================

# Overview of data fields and % Data Missing,
# trend

min_ord_date, max_ord_date = mdl.get_date_range()
cols_dict = mdl.cols_dict

null_cols_comp = [x for x in mdl.get_columns() if x.__contains__('null') and not x.__contains__('cans')]
null_cols_canc = [x for x in mdl.get_columns() if x.__contains__('null') and x.__contains__('cans')]
null_cols_all = [x for x in mdl.get_columns() if x.__contains__('null')]


# dt = date_input("Select a Date", value=max_ord_date, min_value=min_ord_date, max_value=max_ord_date)
dt = max_ord_date
option_comp = [cols_dict[x] for x in null_cols_comp]
seller_name = [x[0] for x in mdl.get_sellers(dt)]


#  Variables Declaration.
# ====================================================================================

df_cc, df_canc = mdl.get_per_col(dt)
@dataclass
class high_miss_np:
    name: str =""
    missing_percentage: float = ""
    high_col: str = ""

#  Detailed Completed
# ====================================================================================

fltr_val = ""
for key in cols_dict.keys():
    if cols_dict[key] == option_comp:
        fltr_val = key
        
# print(f"Columns dictionary is {cols_dict}")

missing_col = mdl.load_missing_pc(dt_val=dt, col_name="null_del_cty", total=0)

df = pd.DataFrame(missing_col)

print(df)

# for x in missing_col:
#     print(x[0], x[1], x[2])
#     print("*"*20)
        
high_np1 = high_miss_np()
high_np2 = high_miss_np()
high_np3 = high_miss_np()
        
try:
    high_np1.name = missing_col[0][0],
    high_np1.missing_percentage = np.round((missing_col[0][1] / missing_col[0][2]) * 100, 2)
    high_np1.high_col = ""
except Exception as e:
    print("Error Getting Value.")
    raise e

try:
    high_np2.name = missing_col[1][0],
    high_np2.missing_percentage = np.round((missing_col[1][1] / missing_col[1][2]) * 100, 2)
    high_np2.high_col = ""
except:
    pass

try:
    high_np3.name = missing_col[2][0],
    high_np3.missing_percentage = np.round((missing_col[2][1] / missing_col[2][2]) * 100, 2)
    high_np3.high_col = ""
except:
    pass


print(high_np1)