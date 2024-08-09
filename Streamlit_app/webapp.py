import streamlit as st
import models as mdl
import numpy as np

#  Dashboard Elements
# ====================================================

# Overview of data fields and % Data Missing,
# trend

min_ord_date, max_ord_date = mdl.get_date_range()
cols_dict = cols_dict = {
    "curr_date": "Current Date",
    "ord_date": "Order Date",
    "seller_np": "Seller NP",
    "null_fulfilment_id": "Fulfilment ID",
    "null_net_tran_id": "Net Transaction ID",
    "null_qty": "Quantity",
    "null_itm_fulfilment_id": "Item Fulfilment ID",
    "null_del_pc": "Delivery Pincode",
    "null_created_date_time": "Created Date",
    "null_domain": "Domain",
    "null_del_cty": "Delivery City",
    "null_cans_code": "Cancellation Code",
    "null_cans_dt_time": "Cancellation Date",
    "null_ord_stats": "Order Status",
    "null_fulfil_status": "Fulfilment Status",
    "null_itm_cat": "Item Category",
    "null_cat_cons": "Category",
    "null_sell_pincode": "Seller Pincode",
    "null_prov_id": "Provider ID",
    "null_itm_id": "Item ID",
    "null_sell_np": "Null Seller NP",
    "null_net_ord_id": "Network Order ID",
    "null_sell_cty": "Seller City"
}

null_cols_comp = [x for x in mdl.get_columns() if x.__contains__('null') and not x.__contains__('cans')]
null_cols_canc = [x for x in mdl.get_columns() if x.__contains__('null') and x.__contains__('cans')]
null_cols_all = [x for x in mdl.get_columns() if x.__contains__('null')]

#  Sidebar and Title Elements
# ====================================================================================

with st.sidebar:
    dt = st.date_input("Select a Date", value=max_ord_date, min_value=min_ord_date, max_value=max_ord_date)
    option_comp = st.selectbox("Column Name ", [cols_dict[x] for x in null_cols_comp], index=10)
    seller_name = st.selectbox("Seller NP", [x[0] for x in mdl.get_sellers(dt)])

st.title('OD Data Quality Report')
st.write(f"""For : {dt.strftime("%Y-%m-%d")}""")
st.write(option_comp)
tab_hm, tab_det, tab_can, tab_trend = st.tabs(["% Missing Data", "Detail Completed", "Detail Cancelled", "Trend"])

#  Detailed Column-wise Missing values
# ====================================================================================

df_cc, df_canc = mdl.get_per_col(dt)

with tab_hm:
    with st.container(border=True):
        first_4 = st.columns(4)
        second_4 = st.columns(4)
        third_4 = st.columns(4)
        fourth_4 = st.columns(4)
        last = st.columns(2)

        for i, col in enumerate(first_4 + second_4):
            tile = col.container(height=150)
            if null_cols_comp[i] in cols_dict.keys():
                tile.write(cols_dict[null_cols_comp[i]])
            val = np.round((df_cc[null_cols_comp[i]].sum() / df_cc['total_orders'].sum()) * 100, 2)
            if val > 0:
                tile.write(":red_circle:")
            tile.write(val)

        for i, col in enumerate(third_4 + fourth_4):
            tile = col.container(height=150)
            try:
                if null_cols_comp[i] in cols_dict.keys():
                    tile.write(cols_dict[null_cols_comp[8 + i]])
                    val = np.round((df_cc[null_cols_comp[8 + i]].sum() / df_cc['total_orders'].sum()) * 100, 2)
                    if val > 0:
                        tile.write(":red_circle:")
                    tile.write(val)
            except:
                continue

        for i, col in enumerate(last):
            tile = col.container(height=150)
            try:
                if null_cols_comp[i] in cols_dict.keys():
                    tile.write(cols_dict[null_cols_comp[16 + i]])
                    val = np.round((df_cc[null_cols_comp[16 + i]].sum() / df_cc['total_orders'].sum()) * 100, 2)
                    if val > 0:
                        tile.write(":red_circle:")
                    tile.write(val)
            except:
                continue

#  Detailed Completed
# ====================================================================================

fltr_val = ""
for key in cols_dict.keys():
    if cols_dict[key] == option_comp:
        fltr_val = key

with tab_det:
    if not fltr_val.__contains__("cans"):
        st.write(f"Sellers with Highest Missing {option_comp}.")
        missing_col = mdl.load_missing_pc(dt_val=dt, col_name=fltr_val, total=0)
        
        
        if missing_col:
            col1, col2, col3 = st.columns(3)

            try:
                col1.metric(label=missing_col[0][0],
                            value=str(round((missing_col[0][1] / missing_col[0][2]) * 100, 2)) + "%",
                            delta="5% Threshold")
            except:
                pass

            try:
                col2.metric(label=missing_col[1][0],
                            value=str(round((missing_col[1][1] / missing_col[1][2]) * 100, 2)) + "%",
                            delta="5% Threshold")
            except:
                pass

            try:
                col3.metric(label=missing_col[2][0],
                            value=str(round((missing_col[2][1] / missing_col[2][2]) * 100, 2)) + "%",
                            delta="5% Threshold")
            except:
                pass

            st.table(missing_col)
        else:
            st.write(f"{option_comp} has 'no missing value' for {dt}.")

#  Detailed Cancellation
# ====================================================================================

with tab_can:
    for i, col in enumerate(st.columns((df_canc.shape[1] - 1))):
        tile = col.container(height=150)
        tile.write(cols_dict[null_cols_canc[i]])
        val = np.round((df_canc[null_cols_canc[i]].sum() / df_canc['total_canceled_orders'].sum()) * 100, 2)
        tile.write(val)
        if val > 0:
            tile.write(":red_circle:")

    st.write(f"Sellers with Highest Missing {option_comp}.")
    missing_col = mdl.load_cancelled_orders(dt_val=dt, total=0)

    if missing_col:
        col1, col2, col3 = st.columns(3)

        try:
            col1.metric(label=missing_col[0][0],
                        value=str(round((missing_col[0][1] / missing_col[0][2]) * 100, 2)) + "%",
                        delta="5% Threshold")
        except:
            pass

        try:
            col2.metric(label=missing_col[1][0],
                        value=str(round((missing_col[1][1] / missing_col[1][2]) * 100, 2)) + "%",
                        delta="5% Threshold")
        except:
            pass

        try:
            col3.metric(label=missing_col[2][0],
                        value=str(round((missing_col[2][1] / missing_col[2][2]) * 100, 2)) + "%",
                        delta="5% Threshold")
        except:
            pass

        st.table(missing_col)
    else:
        st.write(f"{option_comp} has 'no missing value' for {dt}.")

#  Trend
# ====================================================================================

with tab_trend:
    curr_df = mdl.get_all_df(dt)
    st.area_chart(curr_df[['ord_date', 'null_del_cty',
                           'null_cans_code', 'null_itm_cat',
                           'null_cat_cons', 'null_sell_pincode',
                           'null_sell_cty']].groupby(by="ord_date").sum())

    st.area_chart(curr_df[['ord_date',
                           'null_itm_fulfilment_id',
                           'null_del_pc', 'null_fulfil_status']].groupby(by="ord_date").sum())