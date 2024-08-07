def write_dq_data():
    try:
        app_logger.info("Connecting to Athena to get Data Quality Report.")
        conn_src_athena = connect(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
            s3_staging_dir=os.getenv('S3_STAGING_DIR'),
            region_name=os.getenv('AWS_REGION'),
            schema_name=os.getenv('SCHEMA_NAME')
        )
    except Exception as e:
        print(e.args[0])
        sys.exit()
    else:
        app_logger.info("Connected to Athena Database.")

    try:
        app_logger.info("Connecting to Target Postgres DB.")
        conn_tgt_pg = get_postgres_connection()
    except Exception as e:
        print(e.args[0])
        sys.exit()
    else:
        app_logger.info("Connected to target Postgres Database")

    to_run_src = utils.read_clean_script(script_loc + "//" + "6.1_Sel_DQ_Rep.sql")

    try:
        result = conn_src_athena.cursor().execute(to_run_src).fetchall()
    except Exception as e:
        print(e.args[0])
        sys.exit()
    else:
        app_logger.info("Got Data from Athena.")
        # print(result)

    tgt_qry = utils.read_clean_script(script_loc + "//" + "6.2_INS_DQ_Rep.sql")

    try:
        conn_tgt_pg.cursor().executemany(tgt_qry, result)
    except Exception as e:
        print(e.args[0])
    else:
        conn_tgt_pg.commit()
        app_logger.info("Written the data to db.")
        conn_tgt_pg.close()
        conn_src_athena.close()
        
        
sel_dq_qry = """
select
	current_date as curr_date,
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) as ord_date,
	"seller np name" AS seller_np,
    SUM(CASE WHEN "Fulfillment Id" IS NULL THEN 1 ELSE 0 END) AS null_fulfilment_id,
    SUM(CASE WHEN "Network Transaction Id" IS NULL THEN 1 ELSE 0 END) AS null_net_tran_id,
    SUM(CASE WHEN "Qty" IS NULL THEN 1 ELSE 0 END) AS null_qty,
    SUM(CASE WHEN "Item Fulfillment Id" IS NULL THEN 1 ELSE 0 END) AS null_itm_fulfilment_id,
    SUM(CASE WHEN "Delivery Pincode" IS NULL OR 'Delivery Pincode' LIKE '%XXX%' THEN 1 ELSE 0 END) AS null_del_pc,
    SUM(CASE WHEN "O_Created Date & Time" IS NULL THEN 1 ELSE 0 END) AS null_created_date_time,
    SUM(CASE WHEN "Domain" IS NULL THEN 1 ELSE 0 END) AS null_domain,
    SUM(CASE WHEN "Delivery City" IS NULL OR "Delivery City" LIKE '%XXX%' THEN 1 ELSE 0 END) AS null_del_cty,
    SUM(CASE WHEN ("Order Status"='Cancelled') AND ("Cancellation Code" IS NULL  OR "Cancellation Code" LIKE '%Item Out of Stock%' OR "Cancellation Code" LIKE '%std:011%')THEN 1 ELSE 0 END) AS null_cans_code,
    SUM(CASE WHEN "Order Status"='Cancelled' AND "F_Cancelled At Date & Time" IS NULL THEN 1 ELSE 0 END) AS null_cans_dt_time,
    SUM(CASE WHEN "Order Status" IS NULL THEN 1 ELSE 0 END) AS null_ord_stats,
    SUM(CASE WHEN "Fulfillment Status" IS NULL THEN 1 ELSE 0 END) AS null_fulfil_status,
    SUM(CASE WHEN "Item Category" IS NULL THEN 1 ELSE 0 END) AS null_itm_cat,
    SUM(CASE WHEN "Item Consolidated Category" IS NULL THEN 1 ELSE 0 END) AS null_cat_cons,
    SUM(CASE WHEN "Seller Pincode" IS NULL OR "Seller Pincode" LIKE '%XXXX%' THEN 1 ELSE 0 END) AS null_sell_pincode,
    SUM(CASE WHEN "Provider id" IS NULL THEN 1 ELSE 0 END) AS null_prov_id,
    SUM(CASE WHEN "item id" IS NULL THEN 1 ELSE 0 END) AS null_itm_id,
    SUM(CASE WHEN "seller np name" IS NULL THEN 1 ELSE 0 END) AS null_sell_np,
    SUM(CASE WHEN "network order id" IS NULL THEN 1 ELSE 0 END) AS null_net_ord_id,
    SUM(CASE WHEN "seller city" IS NULL THEN 1 ELSE 0 END) AS null_sell_cty,
    count(*) as total_orders,
    SUM(CASE WHEN "Order Status" = 'Cancelled' THEN 1 ELSE 0 END) AS total_canceled_orders
FROM ATH_DB.ATH_TBL_B2C
where
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) = current_date - interval '1' day
GROUP BY
    date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name";
"""

ins_dq_qry = """
insert into POSTGRES_SCHEMA.OD_DQ_TABLE(curr_date,ord_date,seller_np,
null_fulfilment_id,null_net_tran_id,null_qty,null_itm_fulfilment_id,
null_del_pc,null_created_date_time,null_domain,null_del_cty,null_cans_code,
null_cans_dt_time, null_ord_stats,null_fulfil_status,null_itm_cat,null_cat_cons,
null_sell_pincode,null_prov_id,null_itm_id,null_sell_np,null_net_ord_id,
null_sell_cty,total_orders,total_canceled_orders)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""