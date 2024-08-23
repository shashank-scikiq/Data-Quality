import os
from dotenv import load_dotenv
load_dotenv()
SCHEMA_SOURCE = os.getenv('SCHEMA_SOURCE')
DATABASE = os.getenv('DATABASE')
START_DATE = os.getenv('START_DATE')


def get_queries(last_run_date):
    queries = {
        "GV_OD_query": f"""select 
                date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_gift_voucher_order' as view_name,
                count(1) as row_count,
                count(distinct "network_order_id") as distinct_order_count from
                (SELECT odv."network order id" AS network_order_id,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."provider_id")))) AS provider_key,
                    SUM(CAST(odv."qty" AS Decimal)) AS total_items,
                    MAX(case WHEN TRIM(odv."Domain") = 'ONDC:FIS10' THEN 'Retail_Voucher' ELSE 'Others' END) AS domain,
                    MAX(case WHEN odv."order_status" IS NULL OR TRIM(odv."order_status") = '' THEN 'In-progress' ELSE TRIM(odv."order_status") END) AS order_status,
                    MAX(case WHEN UPPER(odv."delivery pincode") LIKE '%XXX%' OR UPPER(odv."delivery pincode") LIKE '%*%' THEN null ELSE odv."delivery pincode" END) AS delivery_pincode,
                    MAX(DATE(odv."o_created_at_date")) AS order_date,
                    NULL as delivery_state,
                    NULL as delivery_state_code, 
                    NULL as delivery_district
                FROM {DATABASE}.shared_open_data_gift_voucher_order odv
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and (DATE(odv."o_created_at_date")) >= DATE('{START_DATE}')
                GROUP BY odv."network order id") group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') """,

        "B2B_OD_query": f"""select 
                date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_b2b_order' as view_name,
                count(1) as row_count,
                count(distinct "network_order_id") as distinct_order_count from(
                SELECT odv."network order id" AS network_order_id,
                    MAX(odv."seller np name") AS seller_np,
                    SUM(CAST(odv."qty" AS Decimal)) AS total_items,MAX(case WHEN TRIM(odv."Domain") = 'ONDC:RET10' THEN 'B2B' ELSE 'Others' END) AS domain,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."provider_id")))) AS provider_key,
                    MAX(case WHEN odv."order status" IS NULL OR TRIM(odv."order status") = '' THEN 'In-progress' ELSE TRIM(odv."order status") END) AS order_status,
                    MAX(case WHEN UPPER(odv."Delivery Pincode") LIKE '%XXX%' OR UPPER(odv."Delivery Pincode") LIKE '%*%' THEN null ELSE odv."Delivery Pincode" END) AS delivery_pincode,
                    MAX(DATE(SUBSTRING(odv."O_Created Date & Time", 1, 10))) AS order_date,
                NULL as delivery_state,
                NULL as delivery_state_code, 
                NULL as delivery_district
                FROM {DATABASE}.shared_open_data_b2b_order  odv
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                GROUP BY odv."network order id") group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "B2C_OD_query": f"""
                select date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'nhm_order_fulfillment_subset_v1' as view_name,
                count(1) as row_count,
                count(distinct "network_order_id") as distinct_order_count from(
                WITH order_subcategories AS (
                    select
                        "network order id", "Item Category" AS sub_category,
                        array_join(cast(array_agg(coalesce("Item Consolidated Category", 'Missing')) as array(varchar)),',') AS consolidated_categories,
                        COUNT(DISTINCT "Item Consolidated Category") AS category_count
                    from
                        (select "network order id", "Item Consolidated Category", "Item Category"
                    from {DATABASE}.nhm_order_fulfillment_subset_v1
                    where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                    and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                    group by "network order id","Item Consolidated Category","Item Category"  )
                    group by "network order id", "Item Category"
                ),
                distinct_subcategories AS (
                select "network order id", "Item Category" AS sub_category
                from {DATABASE}.nhm_order_fulfillment_subset_v1
                where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                group by "network order id", "Item Category"
                )
                SELECT odv."network order id" AS network_order_id,
                    odv."Item Category" AS sub_category,
                    MAX(odv."seller np name") AS seller_np,
                    SUM(CAST(odv."Qty" AS Decimal)) AS total_items,MAX(case WHEN TRIM(odv."Domain") = 'nic2004:52110' THEN 'Retail' ELSE 'Others' END) AS domain,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."Provider id")))) AS provider_key,
                    MAX(case WHEN odv."Order Status" IS NULL OR TRIM(odv."Order Status") = '' THEN 'In-progress' ELSE TRIM(odv."Order Status") END) AS order_status,
                    MAX(CASE WHEN UPPER(odv."Seller Pincode") LIKE '%XXX%' OR UPPER(odv."Seller Pincode") LIKE '%*%' THEN NULL ELSE odv."Seller Pincode" END) AS seller_pincode,
                    MAX(case WHEN UPPER(odv."Delivery Pincode") LIKE '%XXX%' OR UPPER(odv."Delivery Pincode") LIKE '%*%' THEN null ELSE odv."Delivery Pincode" END) AS delivery_pincode,
                    MAX(DATE(SUBSTRING(odv."O_Created Date & Time", 1, 10))) AS order_date,
                    MAX(oc.consolidated_categories) AS consolidated_categories,
                MAX(CASE WHEN oc.category_count > 1 THEN 1 ELSE 0 END) AS multi_category_flag,
                NULL as delivery_state,
                NULL as delivery_state_code, 
                NULL as delivery_district,
                NULL as seller_state,
                NULL as seller_state_code,
                NULL as seller_district
                FROM {DATABASE}.nhm_order_fulfillment_subset_v1  odv
                LEFT JOIN order_subcategories oc ON odv."network order id" = oc."network order id" AND odv."Item Category" = oc.sub_category
                LEFT JOIN distinct_subcategories dc ON odv."network order id" = dc."network order id" AND odv."Item Category" = dc.sub_category
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                GROUP BY odv."network order id", odv."Item Category") group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "logistics_OD_query": f"""select 
                date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_logistics_order' as view_name,
                count(1) as row_count,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_date" AS varchar))) as distinct_order_count from(
                WITH base_data AS (
                    SELECT
                        a.bap_id,
                        a.bpp_id,
                        a.provider_id,
                        a.order_id,
                        a.transaction_id,
                        a.item_id,
                        a.fulfillment_status,
                        date(a.order_created_at) AS order_date,
                        a.domain,
                        date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') AS f_agent_assigned_at_date,
                        CASE
                            WHEN UPPER(a.latest_order_status) = 'COMPLETED' THEN 'Delivered'
                            WHEN UPPER(a.latest_order_status) = 'CANCELLED' THEN 'Cancelled'
                            ELSE 'In Process'
                        END AS Log_Ondc_Status,
                        a.network_retail_order_id,
                        CASE
                            WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                            ELSE a.shipment_type
                        END AS shipment_type,
                        CASE
                            WHEN REGEXP_LIKE(a.pick_up_pincode, '^[0-9]+$') THEN CAST(CAST(a.pick_up_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS pick_up_pincode,
                        CASE
                            WHEN REGEXP_LIKE(a.delivery_pincode, '^[0-9]+$') THEN CAST(CAST(a.delivery_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS delivery_pincode,
                        CASE
                            WHEN a.network_retail_order_category IS NULL THEN 'Undefined'
                            WHEN a.network_retail_order_category = '' THEN 'Undefined'
                            ELSE a.network_retail_order_category
                        END AS network_retail_order_category,
                        a.on_confirm_sync_response,
                        a.on_confirm_error_code,
                        a.on_confirm_error_message,
                        null as delivery_district,
                        null as delivery_state,
                        null as delivery_state_code,
                        null as seller_state,
                        null as seller_district,
                        null as seller_state_code
                    FROM {DATABASE}.shared_open_data_logistics_order  a
                    where
                    not (lower(bpp_id) like '%test%')
                    and not(lower(bap_id) like '%test%')
                    and not(lower(bpp_id) like '%preprod%')
                    and not(lower(bap_id) like '%demoproject%')
                    and not(lower(bpp_id) like '%preprod')
                    and DATE(order_created_at) is not null
                    and DATE(a.order_created_at) >= date('{START_DATE}')
                    and a.bap_id is not null
                    AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                    AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                ),
                filtered_data AS (
                    SELECT
                        a.bap_id,
                        a.bpp_id,
                        a.provider_id,
                        a.order_id,
                        a.transaction_id,
                        a.item_id,
                        a.fulfillment_status,
                        date(a.order_created_at) AS order_date,
                        a.domain,
                        date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') AS f_agent_assigned_at_date,
                        CASE
                            WHEN UPPER(a.latest_order_status) = 'COMPLETED' THEN 'Delivered'
                            WHEN UPPER(a.latest_order_status) = 'CANCELLED' THEN 'Cancelled'
                            ELSE 'In Process'
                        END AS Log_Ondc_Status,
                        a.network_retail_order_id,
                        CASE
                            WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                            ELSE a.shipment_type
                        END AS shipment_type,
                        CASE
                            WHEN REGEXP_LIKE(a.pick_up_pincode, '^[0-9]+$') THEN CAST(CAST(a.pick_up_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS pick_up_pincode,
                        CASE
                            WHEN REGEXP_LIKE(a.delivery_pincode, '^[0-9]+$') THEN CAST(CAST(a.delivery_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS delivery_pincode,
                        CASE
                            WHEN a.network_retail_order_category IS NULL THEN 'Undefined'
                            WHEN a.network_retail_order_category = '' THEN 'Undefined'
                            ELSE a.network_retail_order_category
                        END AS network_retail_order_category,
                        a.on_confirm_sync_response,
                        a.on_confirm_error_code,
                        a.on_confirm_error_message,
                        null as delivery_district,
                        null as delivery_state,
                        null as delivery_state_code,
                        null as seller_state,
                        null as seller_district,
                        null as seller_state_code
                    FROM {DATABASE}.shared_open_data_logistics_order a
                    WHERE date(a.order_created_at) >= DATE('2024-05-01')
                    and date(a.order_created_at) >= date('{START_DATE}')
                        AND date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') IS NULL
                        AND UPPER(a.latest_order_status) = 'CANCELLED'
                        AND (CASE
                                WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                                ELSE a.shipment_type
                            END) = 'P2P'
                    and not (lower(bpp_id) like '%test%')
                    and not(lower(bap_id) like '%test%')
                    and not(lower(bpp_id) like '%preprod%')
                    and not(lower(bap_id) like '%demoproject%')
                    and not(lower(bpp_id) like '%preprod')
                    and a.bap_id is not null
                    and DATE(order_created_at) is not null
                    AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                )SELECT * FROM base_data
                except SELECT * FROM filtered_data)
                group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "GV_NO_query": f"""SELECT date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month,
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 
                'NO_with_base_query' as dashboard, 
                'shared_gift_card_order_fulfillment' as view_name,
                    count(1) as row_count,
                    COUNT(DISTINCT network_order_id) as distinct_order_count
                FROM 
                    {DATABASE}.shared_gift_card_order_fulfillment
                GROUP BY 
                    date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')""",

        "B2B_NO_query": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'NO_with_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count,
                count(distinct "Network order id") as distinct_order_count from
                (with table1 as (
                select
                    "buyer np name",
                    "seller np name",
                    "network order id",
                    "network transaction id",
                    "fulfillment status",
                    "Domain",
                    DATE(SUBSTRING("O_Created Date & Time",
                        1,
                        10)) as "Date",
                    date_parse("o_completed on date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Delivered at",
                    date_parse("o_cancelled at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Cancelled at",
                    date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s') as "Created at",
                    "provider_id",
                    "provider_name",
                    case
                            when "fulfillment status" = 'RTO-Delivered' then '013'
                        when trim("order status") = 'Cancelled'
                        and "cancellation code" is null then '050'
                        when(case
                                when trim("order status") = 'Cancelled' then 'Cancelled'
                            when trim("order status") = 'Completed' then 'Order-delivered'
                            else "fulfillment status"
                        end) = 'Cancelled' then "cancellation code"
                        else null
                    end as "cancellation_code",
                    case
                        when trim("order status") is null then 'In-progress'
                        when trim("order status") = '' then 'In-progress'
                        when trim("order status") like '%**%' then 'In-progress'
                        else trim("order status")
                    end as "Order Status",
                        case
                        when trim("order status") = 'Completed' then 'Delivered'
                        when trim("order status") like '%Return%' then 'Delivered'
                        when trim("order status") = 'Cancelled' then 'Cancelled'
                        else 'In Process'
                    end as "ONDC order_status",
                    case
                        when upper("Delivery city") like '%XXX%' then 'Undefined'
                        when upper("Delivery city") like '' then 'Undefined'
                        when upper("Delivery city") like '%*%' then 'Undefined'
                        when upper("Delivery city") like 'null' then 'Undefined'
                        when upper("Delivery city") is null then 'Undefined'
                        else "Delivery city"
                    end as "Delivery city",
                    case
                        when upper("Delivery Pincode") like '%XXX%' then 'Undefined'
                        when upper("Delivery Pincode") like '' then 'Undefined'
                        when upper("Delivery Pincode") like '%*%' then 'Undefined'
                        when upper("Delivery Pincode") like 'null' then 'Undefined'
                        when upper("Delivery Pincode") is null then 'Undefined'
                        else "Delivery Pincode"
                    end as "Delivery Pincode",
                    case
                        when "Promised time to deliver Date & Time from on_select" is null then 1
                        else 0
                    end as "TAT null",
                    "qty",
                    date_parse("f_order-picked-up at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Shipped at",
                        date_parse("f_packed at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Ready to Ship",
                        date_parse("Promised time to deliver Date & Time from on_select",
                        '%Y-%m-%dT%H:%i:%s') as "Promised time"
                from
                    {DATABASE}.shared_hudi_b2b_order_fullfillment_view)
                select
                    "buyer np name",
                    "seller np name",
                    "network order id",
                    "network transaction id",
                    "Delivery city",
                    "Delivery Pincode",
                    "provider_id",
                    "TAT null",
                    ARRAY_JOIN(ARRAY_AGG(distinct("Domain")),
                    ',')as "Domain",
                    ARRAY_JOIN(ARRAY_AGG(distinct("fulfillment status")),
                    ',')as "fulfillment status",
                    ARRAY_JOIN(ARRAY_AGG(distinct("Order Status")),
                    ',')as "Order Status",
                    ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                    ',')as "ONDC order_status",
                    max("Date") as "Date",
                    max("Delivered at") as "Delivered at",
                    max("Cancelled at") as "Cancelled at",
                    max("Created at") as "Created at",
                        case
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Delivered' and max("Delivered at") is null then max("Created at")
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Delivered' then max("Delivered at")
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Cancelled' then max("Cancelled at")
                        else max("Created at")
                    end as "Updated at",
                    max("cancellation_code") as "cancellation_code",
                    max("Shipped at") as "Shipped at",
                    max("Ready to Ship") as "Ready to Ship",
                    coalesce(max("Promised time"),
                    max("Created at")) as "Promised time",
                        max("provider_name") as "Provider name",
                    sum(cast("qty" as bigint)) as "qty"
                from
                    table1
                group by
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8) group by date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "B2C_NO_query": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'NO_with_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count,
                count(distinct "Network order id") as distinct_order_count from (
                with bottom_layer as (
                select *,
                    case
                        when "fulfillment status" like '%RTO%' and ("cancellation code" is null or "f_cancellation_code" is null) then '013'
                        when "cancellation code" is null then null
                    when substring("cancellation code",-3, 4) not in ('001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016',
                '017', '018', '019', '020', '021', '022') then '052'
                    else substring("cancellation code",-3, 4)
                end as "cancel_code",
                    case
                        when "f_cancellation_code" is null then null
                    when substring("f_cancellation_code",-3, 4) not in ('001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016',
                '017', '018', '019', '020', '021', '022') then '052'
                    else substring("f_cancellation_code",-3, 4)
                end as "f_cancel_code"
                from
                    {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi
                where
                    date(date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s')) >= date('{START_DATE}')
                    and "network order id" is not null
                    and "network order id" <> ''
                    and not (
                lower("buyer np name") like '%stg%'
                        or lower("buyer np name") like '%preprod%'
                            or lower("buyer np name") like '%pre-prod%'
                                or lower("buyer np name") like 'buyer-refapp-ops.ondc.org'
                                    or lower("buyer np name") like '%staging%'
                                        or lower("buyer np name") like '%testing%'
                                            or lower("buyer np name") like '%test%' )
                    and not (
                lower("seller np name") like '%rapidor%'
                        or lower("seller np name") like '%staging%'
                            or lower("seller np name") like '%preprod%'
                                or lower("seller np name") like '%pre-prod%'
                                    or lower("seller np name") like 'gl-6912-httpapi.glstaging.in/gl/ondc'
                                        or lower("seller np name") like '%testing%'
                                            or lower("seller np name") like '%test%'
                                                or lower("seller np name") like '%ultron%')),	
                base_table as (
                select
                    "network order id",
                    "buyer np name",
                    case
                        when "seller np name" like '%kiko%' then 'ondc.kiko.live/ondc-seller'
                        else "seller np name"
                    end as "seller np name",
                    "fulfillment status",
                    case 
                        when "on_confirm_sync_response" is null then 'NULL'
                        else "on_confirm_sync_response"
                    end as "on_confirm_sync_response",
                    case 
                        when "on_confirm_error_code" is null then 'NULL'
                        else "on_confirm_error_code"
                    end as "on_confirm_error_code",
                    coalesce("cancel_code","f_cancel_code",'050')as "cancellation_code",
                    "f_rto_requested_at",
                    row_number() over (partition by ("network order id" ||
                        (case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end))
                order by
                        (
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end) ) max_record_key,
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end as "item consolidated category",
                    "domain",
                    date_parse("o_completed on date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Completed at",
                    date_parse("o_cancelled at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Cancelled at",
                    date_parse("f_order-picked-up at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Shipped at",
                        date_parse("f_packed at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Ready to Ship",
                        date_parse("Promised time to deliver Date & Time from on_select",
                        '%Y-%m-%dT%H:%i:%s') as "Promised time",
                    "Delivery Pincode",
                    date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s') as "Created at",
                    date(date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s')) as "Date",
                    "provider_id",
                    "seller pincode",
                    "seller name",
                    date_parse("F_Order Delivered at Date & Time From Fulfillments",
                        '%Y-%m-%dT%H:%i:%s') as "Completed at Ful",
                    case
                        when not("order status" in ('Cancelled', 'Completed')
                        or ("order status" like '%Return%')) then 
                    (case
                            when ("o_completed on date & time" is not null
                            or "F_Order Delivered at Date & Time From Fulfillments" is not null)
                            and "o_cancelled at date & time" is null then 'Completed'
                            when "o_completed on date & time" is null
                            and "F_Order Delivered at Date & Time From Fulfillments" is null
                            and "o_cancelled at date & time" is not null then 'Cancelled'
                            when ("o_completed on date & time" is not null
                            or "F_Order Delivered at Date & Time From Fulfillments" is not null)
                            and "o_cancelled at date & time" is not null then "order status"
                            else "order status"
                        end)
                        else "order status"
                    end as "order status"
                from
                    bottom_layer),								
                table1 as (
                select
                    "seller np name" as "Seller NP",
                        "buyer np name" as "Buyer NP",
                        "max_record_key",
                        "domain",
                        "Created at",
                        "Shipped at",
                        "Ready to Ship",
                        "on_confirm_sync_response",
                        "on_confirm_error_code",
                        coalesce(case
                        when "item consolidated category" = 'F&B' then "Promised time" + interval '5' minute
                        else "Promised time"
                    end,
                    "Created at") as "Promised time",
                        "Date",
                        "fulfillment status",
                        "item consolidated category",
                        "network order id" as "Network order id",
                        case
                        when trim("order status") is null then 'In-progress'
                        when trim("order status") = '' then 'In-progress'
                        when trim("order status") like '%**%' then 'In-progress'
                        else trim("order status")
                    end as "Order Status",
                        case
                        when trim(lower("order status")) = 'completed' then 'Delivered'
                        when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                        when trim("order status") like '%Return%' then 'Delivered'
                        when trim(lower("order status")) = 'cancelled' then 'Cancelled'
                        else 'In Process'
                    end as "ONDC order_status",
                case
                        when "fulfillment status" like '%RTO%' then coalesce("cancellation_code",'013')
                    when (case
                            when trim("order status") = 'Cancelled' then 'Cancelled'
                            else "fulfillment status" end) = 'Cancelled' then coalesce("cancellation_code",'050')
                    else null
                end as "cancellation_code",
                            case
                                when (case
                                    when trim("order status") = 'Completed' then 'Delivered'
                            when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                            when trim("order status") like '%Return%' then 'Delivered'
                            when trim("order status") = 'Cancelled' then 'Cancelled'
                            else 'In Process'
                        end) = 'Delivered' then coalesce("Completed at Ful",
                                "Completed at")
                        else null
                    end as "Completed at",
                            case
                                when (case
                            when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                            when trim(lower("order status")) = 'cancelled' then 'Cancelled'
                            else null
                        end) = 'Cancelled' then "Cancelled at"
                        else null
                    end as "Cancelled at",
                            provider_id ,
                            case
                                when upper("seller pincode") like '%XXX%' then 'Undefined'
                        when upper("seller pincode") like '' then 'Undefined'
                        when upper("seller pincode") like '%***%' then 'Undefined'
                        when upper("seller pincode") like 'null' then 'Undefined'
                        when upper("seller pincode") is null then 'Undefined'
                        else "seller pincode"
                    end as "Seller Pincode",
                            case
                                when upper("Delivery Pincode") like '%XXX%' then 'Undefined'
                        when upper("Delivery pincode") like '' then 'Undefined'
                        when upper("Delivery Pincode") like '%***%' then 'Undefined'
                        when upper("Delivery Pincode") like 'null' then 'Undefined'
                        when upper("Delivery Pincode") is null then 'Undefined'
                        else "Delivery Pincode"
                    end as "Delivery Pincode",
                            lower(trim("seller name")) as "seller name"
                from
                            base_table),
                merger_table as (
                select
                    "Network order id",
                    ARRAY_JOIN(ARRAY_AGG(distinct "on_confirm_sync_response"
                order by
                    "on_confirm_sync_response"),
                    ',') as "on_confirm_response",
                    ARRAY_JOIN(ARRAY_AGG(distinct "on_confirm_error_code"
                order by
                    "on_confirm_error_code"),
                    ',') as "on_confirm_error_code",
                    ARRAY_JOIN(ARRAY_AGG(distinct "domain"
                order by
                    "domain"),
                    ',') as "domain",
                    ARRAY_JOIN(ARRAY_AGG(distinct "ONDC order_status"
                order by
                    "ONDC order_status"),
                    ',') as "ONDC order_status",
                    ARRAY_JOIN(ARRAY_AGG(distinct "item consolidated category"
                order by
                    "item consolidated category"),
                    ',') as "item consolidated category"
                from
                    table1
                group by
                    1),
                trial as 
                (
                select
                    t1."Buyer NP",
                    t1."Seller NP",
                    t1."Created at",
                    t1."Network order id",
                    t1."seller name",
                    t1."Shipped at",
                    t1."Ready to Ship",
                    t1."Promised time",
                    t1."Date",
                    t1."Order Status",
                    t1."cancellation_code",
                    t1."Completed at",
                    t1."Cancelled at",
                    t1."provider_id",
                    t1."Seller Pincode",
                    t1."Delivery Pincode",
                    t1."max_record_key",
                    mt."on_confirm_response",
                    mt."on_confirm_error_code",
                    mt."domain",
                    mt."ONDC order_status",
                    mt."item consolidated category"
                from
                    table1 t1
                join merger_table mt on
                    t1."Network order id" = mt."Network order id"),
                last_table as (
                select
                    *
                from
                    trial
                where
                    max_record_key = 1),
                table_l as (
                select
                    "Buyer NP",
                    "Seller NP",
                    "Network order id",
                    "on_confirm_response",
                    "on_confirm_error_code",
                    "domain",
                    "item consolidated category" as "Consolidated_category",
                    case
                        when "ONDC order_status" like '%,%' then 'In Process'
                        else "ONDC order_status"
                    end as "ONDC order_status",	
                    case
                        when "item consolidated category" like '%F&B%'
                            and "item consolidated category" like '%Undefined%' then 'F&B'
                            when "item consolidated category" like '%,%' then 'Multi Category'
                            else "item consolidated category"
                        end as "Category",
                        concat("Seller NP", '_', LOWER("provider_id")) as "provider key",
                        ARRAY_JOIN(ARRAY_AGG(distinct "provider_id" order by "provider_id"),',') as "Provider Id",
                        ARRAY_JOIN(ARRAY_AGG(distinct "seller name" order by "seller name"),',') as "Seller Name",
                        max("Seller Pincode") as "Seller Pincode",
                        max("Delivery Pincode") as "Delivery Pincode",
                        MIN("cancellation_code") as "cancellation_code",
                        max("Created at") as "Created at",
                        max("Date") as "Date",
                        max("Shipped at") as "Shipped at",
                        max("Completed at") as "Completed at",
                        max("Cancelled at") as "Cancelled at",
                        max("Ready to Ship") as "Ready to Ship",
                        max("Promised time") as "Promised time",
                        DATE_DIFF('second',
                        max("Promised time"),
                        max("Completed at")) as "tat_dif",
                        DATE_DIFF('day',
                        max("Promised time"),
                        max("Completed at")) as "tat_diff_days",
                        DATE_DIFF('day',
                        max("Created at"),
                        max("Completed at")) as "day_diff",
                        DATE_DIFF('minute',
                        max("Created at"),
                        max("Completed at")) as "min_diff",
                        DATE_DIFF('minute',
                        max("Created at"),
                        max("Promised time")) as "tat_time",
                        case
                            when row_number() over (partition by "Network order id"
                        order by
                                MAX("Date") desc) > 1 then 0
                            else 1
                        end as "no_key"
                    from
                        last_table
                    group by
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10)
                select
                    "Buyer NP",
                    "Seller NP",
                    "Network order id",
                    "provider key",
                    "Provider Id",
                    "Seller Name",
                    "Seller Pincode",
                    "Delivery Pincode",
                    "cancellation_code",
                    "Created at",
                    "Date",
                    "domain",
                    case
                        when ("ONDC order_status" = 'Delivered'
                            and ("Completed at" <= "Promised time")
                                and "Completed at" is not null) then 1
                        else 0
                    end as "on-time-del",
                    "Shipped at",
                    "Ready to Ship",
                    "Promised time",
                    "tat_dif",
                    "tat_diff_days",
                    "day_diff",
                    "min_diff",
                    "tat_time",
                    "no_key",
                    "ONDC order_status",
                    case
                        when "ONDC order_status" = 'Delivered' then "Completed at"
                        when "ONDC order_status" = 'Cancelled' then "Cancelled at"
                        else "Created at"
                    end as "Updated at",
                    "Category",
                    "Consolidated_category",
                    "on_confirm_response",
                    "on_confirm_error_code"
                from
                    table_l) group by date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "logistics_NO_query": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'NO_with_base_query' as dashboard, 'shared_logistics_item_fulfillment_view_with_date' as view_name,
                count(1) as row_count,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))) as distinct_order_count from (
                with table1 as (
                select
                    "network order id" as "Network order id",
                    row_number() over (partition by ("network order id" ||	
                    (case
                    when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc' and trim("item consolidated category") is NULL 	or "item consolidated category" = '' then 'F&B'
                    when "seller np name" like '%uengage%'	and trim("item consolidated category") is null	or "item consolidated category" = '' then 'F&B'
                    when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl' and trim("item consolidated category") is null or "item consolidated category" = '' then 'F&B'
                    when "seller np name" = 'api.kiko.live/ondc-seller'	and trim("item consolidated category") is null	or "item consolidated category" = '' then 'Grocery'
                    when "seller np name" like '%snapdeal%'	and trim("item consolidated category") is NULL or "item consolidated category" = '' then 'Fashion'
                    when "item category" = 'F&B' then 'F&B'
                    when "item category" = 'Grocery' then 'Grocery'
                    when trim("item category") is not null
                    and trim("item consolidated category") is null then 'Others'
                    when trim("item category") is null then 'Undefined'
                    else trim("item consolidated category")
                    end))
                order by
                        (
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%snapdeal%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Fashion'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end) ) max_record_key,
                        date_parse("o_accepted at date & time",	'%Y-%m-%dT%H:%i:%s') as "Accepted at"
                from
                    {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi  ---     Retail table
                where
                    date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= date('{START_DATE}')
                    and "network order id" is not null
                    and "network order id" <> ''
                    and not (
                lower("buyer np name") like '%stg%'
                        or lower("buyer np name") like '%preprod%'
                            or lower("buyer np name") like '%pre-prod%'
                                or lower("buyer np name") like 'buyer-refapp-ops.ondc.org'
                                    or lower("buyer np name") like '%staging%'
                                        or lower("buyer np name") like '%testing%'
                                            or lower("buyer np name") like '%test%' )
                    and not (
                lower("seller np name") like '%staging%'
                        or lower("seller np name") like '%preprod%'
                            or lower("seller np name") like '%pre-prod%'
                                or lower("seller np name") like 'gl-6912-httpapi.glstaging.in/gl/ondc'
                                    or lower("seller np name") like '%testing%'
                                        or lower("seller np name") like '%test%'
                                            or lower("seller np name") like '%ultron%')),
                table2 as (
                select
                    "Network order id",
                    max("Accepted at") as "Accepted at"
                from
                    table1
                where
                    max_record_key = 1
                group by
                    1)
                select
                a.bap_id,
                a.bpp_id,
                a.provider_id,
                a.order_id,
                a.fulfillment_id,
                a.transaction_id,
                a.item_id,
                a.fulfillment_status,
                a.fulfillment_type,
                date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s') as order_created_at,
                date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) as "Date",
                a.domain,
                date_parse(a.o_accepted_at_date,'%Y-%m-%dT%H:%i:%s') as o_accepted_at_date,
                date_parse(a.o_in_progress_from_date,'%Y-%m-%dT%H:%i:%s') as o_in_progress_from_date,
                date_parse(a.o_completed_on_date,'%Y-%m-%dT%H:%i:%s') as o_completed_on_date,
                date_parse(a.o_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as o_cancelled_at_date,
                date_parse(a.f_pending_from_date,'%Y-%m-%dT%H:%i:%s') as f_pending_from_date,
                date_parse(a.f_order_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_order_delivered_at_date,
                date_parse(a.f_order_picked_up_date,'%Y-%m-%dT%H:%i:%s') as f_order_picked_up_date,
                date_parse(a.f_out_for_delivery_since_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_delivery_since_date,
                date_parse(a.f_rto_initiated_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_initiated_at_date,
                date_parse(a.f_ready_to_ship_at_date,'%Y-%m-%dT%H:%i:%s') as f_ready_to_ship_at_date,
                CAST(NULLIF(REGEXP_REPLACE(a.cancellation_code, '[^0-9]+', ''), '')AS INTEGER) as cancellation_code,
                date_parse(a.f_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as f_cancelled_at_date,
                date_parse(a.f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') as f_agent_assigned_at_date,
                date_parse(a.f_out_for_pickup_from_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_pickup_from_date,
                date_parse(a.f_pickup_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_failed_at_date,
                date_parse(a.f_at_destination_hub_from_date,'%Y-%m-%dT%H:%i:%s') as f_at_destination_hub_from_date,
                date_parse(a.f_delivery_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_failed_at_date,
                date_parse(a.f_searching_for_agent_from_date,'%Y-%m-%dT%H:%i:%s') as f_searching_for_agent_from_date,
                date_parse(a.f_pickup_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_rescheduled_at_date,
                date_parse(a.f_delivery_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_rescheduled_at_date,
                date_parse(a.f_in_transit_from_date,'%Y-%m-%dT%H:%i:%s') as f_in_transit_from_date,
                date_parse(a.f_rto_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_delivered_at_date,
                date_parse(a."Promised time to deliver",'%Y-%m-%dT%H:%i:%s') as "Promised time to deliver",
                case 
                    when UPPER(a.latest_order_status) = 'COMPLETED' then 'Delivered'
                    when UPPER(a.latest_order_status) = 'CANCELLED' then 'Cancelled'
                    else 'In Process'
                end as Log_Ondc_Status,
                a.network_retail_order_id,
                a.item_category_id,
                CASE 
                    when a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE a.shipment_type END as shipment_type,
                CASE
                        WHEN REGEXP_LIKE(a.pick_up_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as pick_up_pincode,
                CASE
                        WHEN REGEXP_LIKE(a.delivery_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as delivery_pincode,
                case
                    when a.network_retail_order_category is null then 'Undefined'
                    when a.network_retail_order_category = '' then 'Undefined'
                    else a.network_retail_order_category
                end as network_retail_order_category,
                case 
                    when a.item_tat is null then a.category_tat
                    else a.item_tat
                end as tat,
                a.on_confirm_sync_response,
                a.on_confirm_error_code,
                a.on_confirm_error_message,
                a.rts_tat_duration,
                date_parse(a.rts_tat,'%Y-%m-%dT%H:%i:%s') AS rts_tat,
                a.pickup_tat_duration,
                date_parse(a.pickup_tat,'%Y-%m-%dT%H:%i:%s') as pickup_tat,
                a.motorable_distance ,
                a.motorable_distance_type,
                b."Network order id" as "retail_noi",
                b."Accepted at"
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date a
                LEFT join table2 b ON upper(a.network_retail_order_id) = upper(b."network order id")
                --WHERE date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) >= DATE('2024-05-01')
                except 
                select
                a.bap_id,
                a.bpp_id,
                a.provider_id,
                a.order_id,
                a.fulfillment_id,
                a.transaction_id,
                a.item_id,
                a.fulfillment_status,
                a.fulfillment_type,
                date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s') as order_created_at,
                date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) as "Date",
                a.domain,
                date_parse(a.o_accepted_at_date,'%Y-%m-%dT%H:%i:%s') as o_accepted_at_date,
                date_parse(a.o_in_progress_from_date,'%Y-%m-%dT%H:%i:%s') as o_in_progress_from_date,
                date_parse(a.o_completed_on_date,'%Y-%m-%dT%H:%i:%s') as o_completed_on_date,
                date_parse(a.o_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as o_cancelled_at_date,
                date_parse(a.f_pending_from_date,'%Y-%m-%dT%H:%i:%s') as f_pending_from_date,
                date_parse(a.f_order_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_order_delivered_at_date,
                date_parse(a.f_order_picked_up_date,'%Y-%m-%dT%H:%i:%s') as f_order_picked_up_date,
                date_parse(a.f_out_for_delivery_since_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_delivery_since_date,
                date_parse(a.f_rto_initiated_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_initiated_at_date,
                date_parse(a.f_ready_to_ship_at_date,'%Y-%m-%dT%H:%i:%s') as f_ready_to_ship_at_date,
                CAST(NULLIF(REGEXP_REPLACE(a.cancellation_code, '[^0-9]+', ''), '')AS INTEGER) as cancellation_code,
                date_parse(a.f_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as f_cancelled_at_date,
                date_parse(a.f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') as f_agent_assigned_at_date,
                date_parse(a.f_out_for_pickup_from_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_pickup_from_date,
                date_parse(a.f_pickup_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_failed_at_date,
                date_parse(a.f_at_destination_hub_from_date,'%Y-%m-%dT%H:%i:%s') as f_at_destination_hub_from_date,
                date_parse(a.f_delivery_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_failed_at_date,
                date_parse(a.f_searching_for_agent_from_date,'%Y-%m-%dT%H:%i:%s') as f_searching_for_agent_from_date,
                date_parse(a.f_pickup_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_rescheduled_at_date,
                date_parse(a.f_delivery_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_rescheduled_at_date,
                date_parse(a.f_in_transit_from_date,'%Y-%m-%dT%H:%i:%s') as f_in_transit_from_date,
                date_parse(a.f_rto_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_delivered_at_date,
                date_parse(a."Promised time to deliver",'%Y-%m-%dT%H:%i:%s') as "Promised time to deliver",
                case 
                    when UPPER(a.latest_order_status) = 'COMPLETED' then 'Delivered'
                    when UPPER(a.latest_order_status) = 'CANCELLED' then 'Cancelled'
                    else 'In Process'
                end as Log_Ondc_Status,
                a.network_retail_order_id,
                a.item_category_id,
                CASE 
                    when a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE a.shipment_type END as shipment_type,
                CASE
                        WHEN REGEXP_LIKE(a.pick_up_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as pick_up_pincode,
                CASE
                        WHEN REGEXP_LIKE(a.delivery_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END  AS delivery_pincode,
                case
                    when a.network_retail_order_category is null then 'Undefined'
                    when a.network_retail_order_category = '' then 'Undefined'
                    else a.network_retail_order_category
                end as network_retail_order_category,
                case 
                    when a.item_tat is null then a.category_tat
                    else a.item_tat
                end as tat,
                a.on_confirm_sync_response,
                a.on_confirm_error_code,
                a.on_confirm_error_message,
                a.rts_tat_duration,
                date_parse(a.rts_tat,'%Y-%m-%dT%H:%i:%s') AS rts_tat,
                a.pickup_tat_duration,
                date_parse(a.pickup_tat,'%Y-%m-%dT%H:%i:%s') as pickup_tat,
                a.motorable_distance ,
                a.motorable_distance_type,
                b."Network order id" as "retail_noi",
                b."Accepted at"
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date a
                LEFT join table2 b ON upper(a.network_retail_order_id) = upper(b."network order id")
                WHERE date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) >= DATE('2024-05-01')
                AND date_parse(f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') IS NULL
                AND UPPER(latest_order_status) = 'CANCELLED'
                AND (CASE 
                    when bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE shipment_type END) = 'P2P') a WHERE 
                    (a.bap_id NOT IN (
                        'ondcpreprodtest.sellerapp.in', 'integrations-preprod.channelier.com', 'ondcpreprod.sellerapp.in', 
                        'preprod-ondc.viranc.com/p/v1/store', 'ondc.testtoprod.production.com', 'biz.test.bitsila.com'
                    ) or a.bap_id is null)
                AND (a.bpp_id NOT IN ('my.ithinklogistics.com/ondc/preprod', 'ondc-preprod-lsp.olacabs.com', 'preprod.ondc.adloggs.com') or a.bpp_id is null)
                AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                GROUP BY date_format(date_parse(CAST("Date" as VARCHAR), '%Y-%m-%d'), '%Y-%m')
                ORDER BY month""",

        "B2C_L1_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'fact_order_detail' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.fact_order_detail fod 
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "B2B_L1_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'fact_order_detail_b2b' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.fact_order_detail_b2b fodbb  
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "GV_L1_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'retail_voucher_fact_order_detail' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.retail_voucher_fact_order_detail fodbb  
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "logistics_L1_query": f"""
                select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 
                'OD_with_L1_query' as dashboard, 
                'logistics_fact_order_detail' as view_name,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_date" AS varchar))) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.logistics_fact_order_detail
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "B2C_L2_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'district_level_orders' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.district_level_orders dlo  
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "B2B_L2_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'retail_b2b_district_level_orders' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.retail_b2b_district_level_orders  
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "GV_L2_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'retail_voucher_district_level_orders' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.retail_voucher_district_level_orders rvdlo 
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "logistics_L2_query": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_with_L2_query' as dashboard, 'logistics_district_level_orders' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.logistics_district_level_orders ldlo 
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "L3_query_Retail": f"""select concat(order_year ,'-',order_month,'-','01') as month, 
                sub_domain  as sub_domain_name, 'Retail' as domain_name, 'OD_with_L3_query' as dashboard, 'district_wise_monthly_aggregates' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.district_wise_monthly_aggregates dwma where domain_name = 'Retail'
                group by sub_domain, concat(order_year ,'-',order_month,'-','01')""",

        "L3_query_Logistics": f"""select concat(order_year ,'-',order_month,'-','01') as month, 
                'Logistics' as sub_domain_name, 'Logistics'  as domain_name, 'OD_with_L3_query' as dashboard, 'district_wise_monthly_aggregates' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.district_wise_monthly_aggregates dwma where domain_name = 'Logistics'
                group by domain_name, concat(order_year ,'-',order_month,'-','01')""",

        "L3_query_Logistics_LRD": f"""select concat(order_year ,'-',order_month,'-','01') as month,
                'Logistics' as sub_domain_name, 'Logistics'  as domain_name, 'OD_with_L3_query' as dashboard, 'district_wise_monthly_aggregates' as view_name,
                sum(total_orders_delivered) as distinct_order_count,
                count(1) as row_count
                from {SCHEMA_SOURCE}.district_wise_monthly_aggregates dwma where domain_name = 'Logistics'
                group by domain_name, concat(order_year ,'-',order_month,'-','01')""",

        "OD_NO_validation_query": f"""select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count,
                count(distinct "network order id") as distinct_order_count
                from {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard,'shared_b2b_order_fullfillment_view' as view_name,
                count(1) as row_count,
                count(distinct "network order id") as distinct_order_count
                from {DATABASE}.shared_b2b_order_fullfillment_view
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard,'shared_gift_card_order_fulfillment' as view_name,
                count(1) as row_count,
                count(distinct "network_order_id") as distinct_order_count
                from {DATABASE}.shared_gift_card_order_fulfillment
                group by date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')
                union
                select date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'NO_without_base_query' as dashboard,'shared_logistics_item_fulfillment_view_with_date' as view_name,
                count(1) as row_count,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))) as distinct_order_count
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date
                group by date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard, 'nhm_order_fulfillment_subset_v1' as view_name,
                count(1) as row_count,
                count(distinct "network order id") as distinct_order_count
                from {DATABASE}.nhm_order_fulfillment_subset_v1
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_b2b_order' as view_name,
                count(1) as row_count,
                count(distinct "network order id") as distinct_order_count
                from {DATABASE}.shared_open_data_b2b_order
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_gift_voucher_order' as view_name,
                count(1) as row_count,
                count(distinct "network order id") as distinct_order_count
                from {DATABASE}.shared_open_data_gift_voucher_order
                group by date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')
                union
                select date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_logistics_order' as view_name,
                count(1) as row_count,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))) as distinct_order_count
                from {DATABASE}.shared_open_data_logistics_order
                group by date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')""",

        "GV_OD_query_LRD": f"""select date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_gift_voucher_order' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network_order_id") as distinct_order_count_till_last_run_date from
                (SELECT odv."network order id" AS network_order_id,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."provider_id")))) AS provider_key,
                    SUM(CAST(odv."qty" AS Decimal)) AS total_items,
                    MAX(case WHEN TRIM(odv."Domain") = 'ONDC:FIS10' THEN 'Retail_Voucher' ELSE 'Others' END) AS domain,
                    MAX(case WHEN odv."order_status" IS NULL OR TRIM(odv."order_status") = '' THEN 'In-progress' ELSE TRIM(odv."order_status") END) AS order_status,
                    MAX(case WHEN UPPER(odv."delivery pincode") LIKE '%XXX%' OR UPPER(odv."delivery pincode") LIKE '%*%' THEN null ELSE odv."delivery pincode" END) AS delivery_pincode,
                    MAX(DATE(odv."o_created_at_date")) AS order_date,
                    NULL as delivery_state,
                    NULL as delivery_state_code, 
                    NULL as delivery_district
                FROM {DATABASE}.shared_open_data_gift_voucher_order odv
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and (DATE(odv."o_created_at_date")) >= DATE('{START_DATE}')
                GROUP BY odv."network order id") where cast("order_date" as varchar) < '{last_run_date}'
                group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') """,

        "B2B_OD_query_LRD": f"""select date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_b2b_order' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network_order_id") as distinct_order_count_till_last_run_date from(
                SELECT odv."network order id" AS network_order_id,
                    MAX(odv."seller np name") AS seller_np,
                    SUM(CAST(odv."qty" AS Decimal)) AS total_items,MAX(case WHEN TRIM(odv."Domain") = 'ONDC:RET10' THEN 'B2B' ELSE 'Others' END) AS domain,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."provider_id")))) AS provider_key,
                    MAX(case WHEN odv."order status" IS NULL OR TRIM(odv."order status") = '' THEN 'In-progress' ELSE TRIM(odv."order status") END) AS order_status,
                    MAX(case WHEN UPPER(odv."Delivery Pincode") LIKE '%XXX%' OR UPPER(odv."Delivery Pincode") LIKE '%*%' THEN null ELSE odv."Delivery Pincode" END) AS delivery_pincode,
                    MAX(DATE(SUBSTRING(odv."O_Created Date & Time", 1, 10))) AS order_date,
                NULL as delivery_state,
                NULL as delivery_state_code, 
                NULL as delivery_district
                FROM {DATABASE}.shared_open_data_b2b_order  odv
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                GROUP BY odv."network order id") where cast("order_date" as varchar) < '{last_run_date}'
                group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "B2C_OD_query_LRD": f"""select date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_base_query' as dashboard, 'nhm_order_fulfillment_subset_v1' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network_order_id") as distinct_order_count_till_last_run_date from(
                WITH order_subcategories AS (
                    select
                        "network order id", "Item Category" AS sub_category,
                        array_join(cast(array_agg(coalesce("Item Consolidated Category", 'Missing')) as array(varchar)),',') AS consolidated_categories,
                        COUNT(DISTINCT "Item Consolidated Category") AS category_count
                    from
                        (select "network order id", "Item Consolidated Category", "Item Category"
                    from {DATABASE}.nhm_order_fulfillment_subset_v1
                    where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                    and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                    group by "network order id","Item Consolidated Category","Item Category"  )
                    group by "network order id", "Item Category"
                ),
                distinct_subcategories AS (
                select "network order id", "Item Category" AS sub_category
                from {DATABASE}.nhm_order_fulfillment_subset_v1
                where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                and "seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                group by "network order id", "Item Category"
                )
                SELECT odv."network order id" AS network_order_id,
                    odv."Item Category" AS sub_category,
                    MAX(odv."seller np name") AS seller_np,
                    SUM(CAST(odv."Qty" AS Decimal)) AS total_items,MAX(case WHEN TRIM(odv."Domain") = 'nic2004:52110' THEN 'Retail' ELSE 'Others' END) AS domain,
                    MAX(CONCAT(lower(trim(odv."seller np name")), '-', lower(trim(odv."Provider id")))) AS provider_key,
                    MAX(case WHEN odv."Order Status" IS NULL OR TRIM(odv."Order Status") = '' THEN 'In-progress' ELSE TRIM(odv."Order Status") END) AS order_status,
                    MAX(CASE WHEN UPPER(odv."Seller Pincode") LIKE '%XXX%' OR UPPER(odv."Seller Pincode") LIKE '%*%' THEN NULL ELSE odv."Seller Pincode" END) AS seller_pincode,
                    MAX(case WHEN UPPER(odv."Delivery Pincode") LIKE '%XXX%' OR UPPER(odv."Delivery Pincode") LIKE '%*%' THEN null ELSE odv."Delivery Pincode" END) AS delivery_pincode,
                    MAX(DATE(SUBSTRING(odv."O_Created Date & Time", 1, 10))) AS order_date,
                    MAX(oc.consolidated_categories) AS consolidated_categories,
                MAX(CASE WHEN oc.category_count > 1 THEN 1 ELSE 0 END) AS multi_category_flag,
                NULL as delivery_state,
                NULL as delivery_state_code, 
                NULL as delivery_district,
                NULL as seller_state,
                NULL as seller_state_code,
                NULL as seller_district
                FROM {DATABASE}.nhm_order_fulfillment_subset_v1  odv
                LEFT JOIN order_subcategories oc ON odv."network order id" = oc."network order id" AND odv."Item Category" = oc.sub_category
                LEFT JOIN distinct_subcategories dc ON odv."network order id" = dc."network order id" AND odv."Item Category" = dc.sub_category
                WHERE odv."seller np name" NOT IN ('gl-6912-httpapi.glstaging.in/gl/ondc')
                and date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= DATE('{START_DATE}')
                GROUP BY odv."network order id", odv."Item Category") where cast("order_date" as varchar) < '{last_run_date}'
                group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "logistics_OD_query_LRD": f"""select date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_with_base_query' as dashboard, 'shared_open_data_logistics_order' as view_name,
                count(1) as row_count_till_last_run_date,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_date" AS varchar))) as distinct_order_count_till_last_run_date from(
                WITH base_data AS (
                    SELECT
                        a.bap_id,
                        a.bpp_id,
                        a.provider_id,
                        a.order_id,
                        a.transaction_id,
                        a.item_id,
                        a.fulfillment_status,
                        date(a.order_created_at) AS order_date,
                        a.domain,
                        date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') AS f_agent_assigned_at_date,
                        CASE
                            WHEN UPPER(a.latest_order_status) = 'COMPLETED' THEN 'Delivered'
                            WHEN UPPER(a.latest_order_status) = 'CANCELLED' THEN 'Cancelled'
                            ELSE 'In Process'
                        END AS Log_Ondc_Status,
                        a.network_retail_order_id,
                        CASE
                            WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                            ELSE a.shipment_type
                        END AS shipment_type,
                        CASE
                            WHEN REGEXP_LIKE(a.pick_up_pincode, '^[0-9]+$') THEN CAST(CAST(a.pick_up_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS pick_up_pincode,
                        CASE
                            WHEN REGEXP_LIKE(a.delivery_pincode, '^[0-9]+$') THEN CAST(CAST(a.delivery_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS delivery_pincode,
                        CASE
                            WHEN a.network_retail_order_category IS NULL THEN 'Undefined'
                            WHEN a.network_retail_order_category = '' THEN 'Undefined'
                            ELSE a.network_retail_order_category
                        END AS network_retail_order_category,
                        a.on_confirm_sync_response,
                        a.on_confirm_error_code,
                        a.on_confirm_error_message,
                        null as delivery_district,
                        null as delivery_state,
                        null as delivery_state_code,
                        null as seller_state,
                        null as seller_district,
                        null as seller_state_code
                    FROM {DATABASE}.shared_open_data_logistics_order  a
                    where
                    not (lower(bpp_id) like '%test%')
                    and not(lower(bap_id) like '%test%')
                    and not(lower(bpp_id) like '%preprod%')
                    and not(lower(bap_id) like '%demoproject%')
                    and not(lower(bpp_id) like '%preprod')
                    and DATE(order_created_at) is not null
                    and DATE(a.order_created_at) >= date('{START_DATE}')
                    and a.bap_id is not null
                    AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                    AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                ),
                filtered_data AS (
                    SELECT
                        a.bap_id,
                        a.bpp_id,
                        a.provider_id,
                        a.order_id,
                        a.transaction_id,
                        a.item_id,
                        a.fulfillment_status,
                        date(a.order_created_at) AS order_date,
                        a.domain,
                        date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') AS f_agent_assigned_at_date,
                        CASE
                            WHEN UPPER(a.latest_order_status) = 'COMPLETED' THEN 'Delivered'
                            WHEN UPPER(a.latest_order_status) = 'CANCELLED' THEN 'Cancelled'
                            ELSE 'In Process'
                        END AS Log_Ondc_Status,
                        a.network_retail_order_id,
                        CASE
                            WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                            ELSE a.shipment_type
                        END AS shipment_type,
                        CASE
                            WHEN REGEXP_LIKE(a.pick_up_pincode, '^[0-9]+$') THEN CAST(CAST(a.pick_up_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS pick_up_pincode,
                        CASE
                            WHEN REGEXP_LIKE(a.delivery_pincode, '^[0-9]+$') THEN CAST(CAST(a.delivery_pincode AS DOUBLE) AS DOUBLE)
                            ELSE -1
                        END AS delivery_pincode,
                        CASE
                            WHEN a.network_retail_order_category IS NULL THEN 'Undefined'
                            WHEN a.network_retail_order_category = '' THEN 'Undefined'
                            ELSE a.network_retail_order_category
                        END AS network_retail_order_category,
                        a.on_confirm_sync_response,
                        a.on_confirm_error_code,
                        a.on_confirm_error_message,
                        null as delivery_district,
                        null as delivery_state,
                        null as delivery_state_code,
                        null as seller_state,
                        null as seller_district,
                        null as seller_state_code
                    FROM {DATABASE}.shared_open_data_logistics_order a
                    WHERE date(a.order_created_at) >= DATE('2024-05-01')
                    and date(a.order_created_at) >= date('{START_DATE}')
                        AND date_parse(a.f_agent_assigned_at_date, '%Y-%m-%dT%H:%i:%s') IS NULL
                        AND UPPER(a.latest_order_status) = 'CANCELLED'
                        AND (CASE
                                WHEN a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                                ELSE a.shipment_type
                            END) = 'P2P'
                    and not (lower(bpp_id) like '%test%')
                    and not(lower(bap_id) like '%test%')
                    and not(lower(bpp_id) like '%preprod%')
                    and not(lower(bap_id) like '%demoproject%')
                    and not(lower(bpp_id) like '%preprod')
                    and a.bap_id is not null
                    and DATE(order_created_at) is not null
                    AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                )SELECT * FROM base_data
                except SELECT * FROM filtered_data)
                where cast("order_date" as varchar) < '{last_run_date}'
                group by date_format(date_parse(cast("order_date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "GV_NO_query_LRD": f"""SELECT date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month,
                'Voucher' as sub_domain_name, 'Retail' as domain_name, 'NO_with_base_query' as dashboard, 'shared_gift_card_order_fulfillment' as view_name,
                    count(1) as row_count_till_last_run_date,
                    COUNT(DISTINCT network_order_id) as distinct_order_count_till_last_run_date
                FROM 
                    {DATABASE}.shared_gift_card_order_fulfillment
                where CAST(o_created_at_date AS VARCHAR) < '{last_run_date}'
                GROUP BY 
                    date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')""",

        "B2B_NO_query_LRD": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2B' as sub_domain_name, 'Retail' as domain_name, 'NO_with_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "Network order id") as distinct_order_count_till_last_run_date from
                (with table1 as (
                select
                    "buyer np name",
                    "seller np name",
                    "network order id",
                    "network transaction id",
                    "fulfillment status",
                    "Domain",
                    DATE(SUBSTRING("O_Created Date & Time",
                        1,
                        10)) as "Date",
                    date_parse("o_completed on date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Delivered at",
                    date_parse("o_cancelled at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Cancelled at",
                    date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s') as "Created at",
                    "provider_id",
                    "provider_name",
                    case
                            when "fulfillment status" = 'RTO-Delivered' then '013'
                        when trim("order status") = 'Cancelled'
                        and "cancellation code" is null then '050'
                        when(case
                                when trim("order status") = 'Cancelled' then 'Cancelled'
                            when trim("order status") = 'Completed' then 'Order-delivered'
                            else "fulfillment status"
                        end) = 'Cancelled' then "cancellation code"
                        else null
                    end as "cancellation_code",
                    case
                        when trim("order status") is null then 'In-progress'
                        when trim("order status") = '' then 'In-progress'
                        when trim("order status") like '%**%' then 'In-progress'
                        else trim("order status")
                    end as "Order Status",
                        case
                        when trim("order status") = 'Completed' then 'Delivered'
                        when trim("order status") like '%Return%' then 'Delivered'
                        when trim("order status") = 'Cancelled' then 'Cancelled'
                        else 'In Process'
                    end as "ONDC order_status",
                    case
                        when upper("Delivery city") like '%XXX%' then 'Undefined'
                        when upper("Delivery city") like '' then 'Undefined'
                        when upper("Delivery city") like '%*%' then 'Undefined'
                        when upper("Delivery city") like 'null' then 'Undefined'
                        when upper("Delivery city") is null then 'Undefined'
                        else "Delivery city"
                    end as "Delivery city",
                    case
                        when upper("Delivery Pincode") like '%XXX%' then 'Undefined'
                        when upper("Delivery Pincode") like '' then 'Undefined'
                        when upper("Delivery Pincode") like '%*%' then 'Undefined'
                        when upper("Delivery Pincode") like 'null' then 'Undefined'
                        when upper("Delivery Pincode") is null then 'Undefined'
                        else "Delivery Pincode"
                    end as "Delivery Pincode",
                    case
                        when "Promised time to deliver Date & Time from on_select" is null then 1
                        else 0
                    end as "TAT null",
                    "qty",
                    date_parse("f_order-picked-up at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Shipped at",
                        date_parse("f_packed at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Ready to Ship",
                        date_parse("Promised time to deliver Date & Time from on_select",
                        '%Y-%m-%dT%H:%i:%s') as "Promised time"
                from
                    {DATABASE}.shared_hudi_b2b_order_fullfillment_view)
                select
                    "buyer np name",
                    "seller np name",
                    "network order id",
                    "network transaction id",
                    "Delivery city",
                    "Delivery Pincode",
                    "provider_id",
                    "TAT null",
                    ARRAY_JOIN(ARRAY_AGG(distinct("Domain")),
                    ',')as "Domain",
                    ARRAY_JOIN(ARRAY_AGG(distinct("fulfillment status")),
                    ',')as "fulfillment status",
                    ARRAY_JOIN(ARRAY_AGG(distinct("Order Status")),
                    ',')as "Order Status",
                    ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                    ',')as "ONDC order_status",
                    max("Date") as "Date",
                    max("Delivered at") as "Delivered at",
                    max("Cancelled at") as "Cancelled at",
                    max("Created at") as "Created at",
                        case
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Delivered' and max("Delivered at") is null then max("Created at")
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Delivered' then max("Delivered at")
                        when (case
                            when ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',') like '%Process%' then 'In Process'
                            else ARRAY_JOIN(ARRAY_AGG(distinct("ONDC order_status")),
                            ',')
                        end
                        ) = 'Cancelled' then max("Cancelled at")
                        else max("Created at")
                    end as "Updated at",
                    max("cancellation_code") as "cancellation_code",
                    max("Shipped at") as "Shipped at",
                    max("Ready to Ship") as "Ready to Ship",
                    coalesce(max("Promised time"),
                    max("Created at")) as "Promised time",
                        max("provider_name") as "Provider name",
                    sum(cast("qty" as bigint)) as "qty"
                from
                    table1
                group by
                    1,
                    2,
                    3,
                    4,
                    5,
                    6,
                    7,
                    8) where cast("Date" as varchar) < '{last_run_date}'
                    group by date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",
        
        "B2C_NO_query_LRD": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'NO_with_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "Network order id") as distinct_order_count_till_last_run_date from (
                with bottom_layer as (
                select *,
                    case
                        when "fulfillment status" like '%RTO%' and ("cancellation code" is null or "f_cancellation_code" is null) then '013'
                        when "cancellation code" is null then null
                    when substring("cancellation code",-3, 4) not in ('001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016',
                '017', '018', '019', '020', '021', '022') then '052'
                    else substring("cancellation code",-3, 4)
                end as "cancel_code",
                    case
                        when "f_cancellation_code" is null then null
                    when substring("f_cancellation_code",-3, 4) not in ('001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '012', '013', '014', '015', '016',
                '017', '018', '019', '020', '021', '022') then '052'
                    else substring("f_cancellation_code",-3, 4)
                end as "f_cancel_code"
                from
                    {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi
                where
                    date(date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s')) >= date('{START_DATE}')
                    and "network order id" is not null
                    and "network order id" <> ''
                    and not (
                lower("buyer np name") like '%stg%'
                        or lower("buyer np name") like '%preprod%'
                            or lower("buyer np name") like '%pre-prod%'
                                or lower("buyer np name") like 'buyer-refapp-ops.ondc.org'
                                    or lower("buyer np name") like '%staging%'
                                        or lower("buyer np name") like '%testing%'
                                            or lower("buyer np name") like '%test%' )
                    and not (
                lower("seller np name") like '%rapidor%'
                        or lower("seller np name") like '%staging%'
                            or lower("seller np name") like '%preprod%'
                                or lower("seller np name") like '%pre-prod%'
                                    or lower("seller np name") like 'gl-6912-httpapi.glstaging.in/gl/ondc'
                                        or lower("seller np name") like '%testing%'
                                            or lower("seller np name") like '%test%'
                                                or lower("seller np name") like '%ultron%')),	
                base_table as (
                select
                    "network order id",
                    "buyer np name",
                    case
                        when "seller np name" like '%kiko%' then 'ondc.kiko.live/ondc-seller'
                        else "seller np name"
                    end as "seller np name",
                    "fulfillment status",
                    case 
                        when "on_confirm_sync_response" is null then 'NULL'
                        else "on_confirm_sync_response"
                    end as "on_confirm_sync_response",
                    case 
                        when "on_confirm_error_code" is null then 'NULL'
                        else "on_confirm_error_code"
                    end as "on_confirm_error_code",
                    coalesce("cancel_code","f_cancel_code",'050')as "cancellation_code",
                    "f_rto_requested_at",
                    row_number() over (partition by ("network order id" ||
                        (case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end))
                order by
                        (
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end) ) max_record_key,
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%dominos%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%agrevolution%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%enam.gov%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Agriculture'
                        when "seller np name" like '%crofarm%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%rebelfoods%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end as "item consolidated category",
                    "domain",
                    date_parse("o_completed on date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Completed at",
                    date_parse("o_cancelled at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Cancelled at",
                    date_parse("f_order-picked-up at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Shipped at",
                        date_parse("f_packed at date & time",
                        '%Y-%m-%dT%H:%i:%s') as "Ready to Ship",
                        date_parse("Promised time to deliver Date & Time from on_select",
                        '%Y-%m-%dT%H:%i:%s') as "Promised time",
                    "Delivery Pincode",
                    date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s') as "Created at",
                    date(date_parse("O_Created Date & Time",
                        '%Y-%m-%dT%H:%i:%s')) as "Date",
                    "provider_id",
                    "seller pincode",
                    "seller name",
                    date_parse("F_Order Delivered at Date & Time From Fulfillments",
                        '%Y-%m-%dT%H:%i:%s') as "Completed at Ful",
                    case
                        when not("order status" in ('Cancelled', 'Completed')
                        or ("order status" like '%Return%')) then 
                    (case
                            when ("o_completed on date & time" is not null
                            or "F_Order Delivered at Date & Time From Fulfillments" is not null)
                            and "o_cancelled at date & time" is null then 'Completed'
                            when "o_completed on date & time" is null
                            and "F_Order Delivered at Date & Time From Fulfillments" is null
                            and "o_cancelled at date & time" is not null then 'Cancelled'
                            when ("o_completed on date & time" is not null
                            or "F_Order Delivered at Date & Time From Fulfillments" is not null)
                            and "o_cancelled at date & time" is not null then "order status"
                            else "order status"
                        end)
                        else "order status"
                    end as "order status"
                from
                    bottom_layer),								
                table1 as (
                select
                    "seller np name" as "Seller NP",
                        "buyer np name" as "Buyer NP",
                        "max_record_key",
                        "domain",
                        "Created at",
                        "Shipped at",
                        "Ready to Ship",
                        "on_confirm_sync_response",
                        "on_confirm_error_code",
                        coalesce(case
                        when "item consolidated category" = 'F&B' then "Promised time" + interval '5' minute
                        else "Promised time"
                    end,
                    "Created at") as "Promised time",
                        "Date",
                        "fulfillment status",
                        "item consolidated category",
                        "network order id" as "Network order id",
                        case
                        when trim("order status") is null then 'In-progress'
                        when trim("order status") = '' then 'In-progress'
                        when trim("order status") like '%**%' then 'In-progress'
                        else trim("order status")
                    end as "Order Status",
                        case
                        when trim(lower("order status")) = 'completed' then 'Delivered'
                        when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                        when trim("order status") like '%Return%' then 'Delivered'
                        when trim(lower("order status")) = 'cancelled' then 'Cancelled'
                        else 'In Process'
                    end as "ONDC order_status",
                case
                        when "fulfillment status" like '%RTO%' then coalesce("cancellation_code",'013')
                    when (case
                            when trim("order status") = 'Cancelled' then 'Cancelled'
                            else "fulfillment status" end) = 'Cancelled' then coalesce("cancellation_code",'050')
                    else null
                end as "cancellation_code",
                            case
                                when (case
                                    when trim("order status") = 'Completed' then 'Delivered'
                            when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                            when trim("order status") like '%Return%' then 'Delivered'
                            when trim("order status") = 'Cancelled' then 'Cancelled'
                            else 'In Process'
                        end) = 'Delivered' then coalesce("Completed at Ful",
                                "Completed at")
                        else null
                    end as "Completed at",
                            case
                                when (case
                            when trim("fulfillment status") like 'RTO%' then 'Cancelled'
                            when trim(lower("order status")) = 'cancelled' then 'Cancelled'
                            else null
                        end) = 'Cancelled' then "Cancelled at"
                        else null
                    end as "Cancelled at",
                            provider_id ,
                            case
                                when upper("seller pincode") like '%XXX%' then 'Undefined'
                        when upper("seller pincode") like '' then 'Undefined'
                        when upper("seller pincode") like '%***%' then 'Undefined'
                        when upper("seller pincode") like 'null' then 'Undefined'
                        when upper("seller pincode") is null then 'Undefined'
                        else "seller pincode"
                    end as "Seller Pincode",
                            case
                                when upper("Delivery Pincode") like '%XXX%' then 'Undefined'
                        when upper("Delivery pincode") like '' then 'Undefined'
                        when upper("Delivery Pincode") like '%***%' then 'Undefined'
                        when upper("Delivery Pincode") like 'null' then 'Undefined'
                        when upper("Delivery Pincode") is null then 'Undefined'
                        else "Delivery Pincode"
                    end as "Delivery Pincode",
                            lower(trim("seller name")) as "seller name"
                from
                            base_table),
                merger_table as (
                select
                    "Network order id",
                    ARRAY_JOIN(ARRAY_AGG(distinct "on_confirm_sync_response"
                order by
                    "on_confirm_sync_response"),
                    ',') as "on_confirm_response",
                    ARRAY_JOIN(ARRAY_AGG(distinct "on_confirm_error_code"
                order by
                    "on_confirm_error_code"),
                    ',') as "on_confirm_error_code",
                    ARRAY_JOIN(ARRAY_AGG(distinct "domain"
                order by
                    "domain"),
                    ',') as "domain",
                    ARRAY_JOIN(ARRAY_AGG(distinct "ONDC order_status"
                order by
                    "ONDC order_status"),
                    ',') as "ONDC order_status",
                    ARRAY_JOIN(ARRAY_AGG(distinct "item consolidated category"
                order by
                    "item consolidated category"),
                    ',') as "item consolidated category"
                from
                    table1
                group by
                    1),
                trial as 
                (
                select
                    t1."Buyer NP",
                    t1."Seller NP",
                    t1."Created at",
                    t1."Network order id",
                    t1."seller name",
                    t1."Shipped at",
                    t1."Ready to Ship",
                    t1."Promised time",
                    t1."Date",
                    t1."Order Status",
                    t1."cancellation_code",
                    t1."Completed at",
                    t1."Cancelled at",
                    t1."provider_id",
                    t1."Seller Pincode",
                    t1."Delivery Pincode",
                    t1."max_record_key",
                    mt."on_confirm_response",
                    mt."on_confirm_error_code",
                    mt."domain",
                    mt."ONDC order_status",
                    mt."item consolidated category"
                from
                    table1 t1
                join merger_table mt on
                    t1."Network order id" = mt."Network order id"),
                last_table as (
                select
                    *
                from
                    trial
                where
                    max_record_key = 1),
                table_l as (
                select
                    "Buyer NP",
                    "Seller NP",
                    "Network order id",
                    "on_confirm_response",
                    "on_confirm_error_code",
                    "domain",
                    "item consolidated category" as "Consolidated_category",
                    case
                        when "ONDC order_status" like '%,%' then 'In Process'
                        else "ONDC order_status"
                    end as "ONDC order_status",	
                    case
                        when "item consolidated category" like '%F&B%'
                            and "item consolidated category" like '%Undefined%' then 'F&B'
                            when "item consolidated category" like '%,%' then 'Multi Category'
                            else "item consolidated category"
                        end as "Category",
                        concat("Seller NP", '_', LOWER("provider_id")) as "provider key",
                        ARRAY_JOIN(ARRAY_AGG(distinct "provider_id" order by "provider_id"),',') as "Provider Id",
                        ARRAY_JOIN(ARRAY_AGG(distinct "seller name" order by "seller name"),',') as "Seller Name",
                        max("Seller Pincode") as "Seller Pincode",
                        max("Delivery Pincode") as "Delivery Pincode",
                        MIN("cancellation_code") as "cancellation_code",
                        max("Created at") as "Created at",
                        max("Date") as "Date",
                        max("Shipped at") as "Shipped at",
                        max("Completed at") as "Completed at",
                        max("Cancelled at") as "Cancelled at",
                        max("Ready to Ship") as "Ready to Ship",
                        max("Promised time") as "Promised time",
                        DATE_DIFF('second',
                        max("Promised time"),
                        max("Completed at")) as "tat_dif",
                        DATE_DIFF('day',
                        max("Promised time"),
                        max("Completed at")) as "tat_diff_days",
                        DATE_DIFF('day',
                        max("Created at"),
                        max("Completed at")) as "day_diff",
                        DATE_DIFF('minute',
                        max("Created at"),
                        max("Completed at")) as "min_diff",
                        DATE_DIFF('minute',
                        max("Created at"),
                        max("Promised time")) as "tat_time",
                        case
                            when row_number() over (partition by "Network order id"
                        order by
                                MAX("Date") desc) > 1 then 0
                            else 1
                        end as "no_key"
                    from
                        last_table
                    group by
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10)
                select
                    "Buyer NP",
                    "Seller NP",
                    "Network order id",
                    "provider key",
                    "Provider Id",
                    "Seller Name",
                    "Seller Pincode",
                    "Delivery Pincode",
                    "cancellation_code",
                    "Created at",
                    "Date",
                    "domain",
                    case
                        when ("ONDC order_status" = 'Delivered'
                            and ("Completed at" <= "Promised time")
                                and "Completed at" is not null) then 1
                        else 0
                    end as "on-time-del",
                    "Shipped at",
                    "Ready to Ship",
                    "Promised time",
                    "tat_dif",
                    "tat_diff_days",
                    "day_diff",
                    "min_diff",
                    "tat_time",
                    "no_key",
                    "ONDC order_status",
                    case
                        when "ONDC order_status" = 'Delivered' then "Completed at"
                        when "ONDC order_status" = 'Cancelled' then "Cancelled at"
                        else "Created at"
                    end as "Updated at",
                    "Category",
                    "Consolidated_category",
                    "on_confirm_response",
                    "on_confirm_error_code"
                from
                    table_l) where cast("Date" as varchar) < '{last_run_date}'
                    group by date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m')""",

        "logistics_NO_query_LRD": f"""select date_format(date_parse(cast("Date" as varchar) , '%Y-%m-%d'), '%Y-%m') as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'NO_with_base_query' as dashboard, 'shared_logistics_item_fulfillment_view_with_date' as view_name,
                count(1) as row_count_till_last_run_date,
                COUNT(
                    distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))
                ) as distinct_order_count_till_last_run_date from (
                with table1 as (
                select
                        "network order id" as "Network order id",
                        row_number() over (partition by ("network order id" ||	
                        (case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'	and trim("item consolidated category") is NULL 	or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'	and trim("item consolidated category") is null	or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl' and trim("item consolidated category") is null	or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'	and trim("item consolidated category") is null	or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%snapdeal%'	and trim("item consolidated category") is NULL or "item consolidated category" = '' then 'Fashion'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end))
                order by
                        (
                    case
                        when "seller np name" = 'webapi.magicpin.in/oms_partner/ondc'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" like '%uengage%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.esamudaay.com/ondc/sdk/bpp/retail/lespl'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'F&B'
                        when "seller np name" = 'api.kiko.live/ondc-seller'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Grocery'
                        when "seller np name" like '%snapdeal%'
                        and trim("item consolidated category") is null
                        or "item consolidated category" = '' then 'Fashion'
                        when "item category" = 'F&B' then 'F&B'
                        when "item category" = 'Grocery' then 'Grocery'
                        when trim("item category") is not null
                        and trim("item consolidated category") is null then 'Others'
                        when trim("item category") is null then 'Undefined'
                        else trim("item consolidated category")
                    end) ) max_record_key,
                        date_parse("o_accepted at date & time",	'%Y-%m-%dT%H:%i:%s') as "Accepted at"
                from
                    {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi  ---     Retail table
                where
                    date(date_parse("O_Created Date & Time",'%Y-%m-%dT%H:%i:%s')) >= date('{START_DATE}')
                    and "network order id" is not null
                    and "network order id" <> ''
                    and not (
                lower("buyer np name") like '%stg%'
                        or lower("buyer np name") like '%preprod%'
                            or lower("buyer np name") like '%pre-prod%'
                                or lower("buyer np name") like 'buyer-refapp-ops.ondc.org'
                                    or lower("buyer np name") like '%staging%'
                                        or lower("buyer np name") like '%testing%'
                                            or lower("buyer np name") like '%test%' )
                    and not (
                lower("seller np name") like '%staging%'
                        or lower("seller np name") like '%preprod%'
                            or lower("seller np name") like '%pre-prod%'
                                or lower("seller np name") like 'gl-6912-httpapi.glstaging.in/gl/ondc'
                                    or lower("seller np name") like '%testing%'
                                        or lower("seller np name") like '%test%'
                                            or lower("seller np name") like '%ultron%')),
                table2 as (
                select
                    "Network order id",
                    max("Accepted at") as "Accepted at"
                from
                    table1
                where
                    max_record_key = 1
                group by
                    1)
                select
                a.bap_id,
                a.bpp_id,
                a.provider_id,
                a.order_id,
                a.fulfillment_id,
                a.transaction_id,
                a.item_id,
                a.fulfillment_status,
                a.fulfillment_type,
                date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s') as order_created_at,
                date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) as "Date",
                a.domain,
                date_parse(a.o_accepted_at_date,'%Y-%m-%dT%H:%i:%s') as o_accepted_at_date,
                date_parse(a.o_in_progress_from_date,'%Y-%m-%dT%H:%i:%s') as o_in_progress_from_date,
                date_parse(a.o_completed_on_date,'%Y-%m-%dT%H:%i:%s') as o_completed_on_date,
                date_parse(a.o_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as o_cancelled_at_date,
                date_parse(a.f_pending_from_date,'%Y-%m-%dT%H:%i:%s') as f_pending_from_date,
                date_parse(a.f_order_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_order_delivered_at_date,
                date_parse(a.f_order_picked_up_date,'%Y-%m-%dT%H:%i:%s') as f_order_picked_up_date,
                date_parse(a.f_out_for_delivery_since_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_delivery_since_date,
                date_parse(a.f_rto_initiated_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_initiated_at_date,
                date_parse(a.f_ready_to_ship_at_date,'%Y-%m-%dT%H:%i:%s') as f_ready_to_ship_at_date,
                CAST(NULLIF(REGEXP_REPLACE(a.cancellation_code, '[^0-9]+', ''), '')AS INTEGER) as cancellation_code,
                date_parse(a.f_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as f_cancelled_at_date,
                date_parse(a.f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') as f_agent_assigned_at_date,
                date_parse(a.f_out_for_pickup_from_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_pickup_from_date,
                date_parse(a.f_pickup_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_failed_at_date,
                date_parse(a.f_at_destination_hub_from_date,'%Y-%m-%dT%H:%i:%s') as f_at_destination_hub_from_date,
                date_parse(a.f_delivery_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_failed_at_date,
                date_parse(a.f_searching_for_agent_from_date,'%Y-%m-%dT%H:%i:%s') as f_searching_for_agent_from_date,
                date_parse(a.f_pickup_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_rescheduled_at_date,
                date_parse(a.f_delivery_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_rescheduled_at_date,
                date_parse(a.f_in_transit_from_date,'%Y-%m-%dT%H:%i:%s') as f_in_transit_from_date,
                date_parse(a.f_rto_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_delivered_at_date,
                date_parse(a."Promised time to deliver",'%Y-%m-%dT%H:%i:%s') as "Promised time to deliver",
                case 
                    when UPPER(a.latest_order_status) = 'COMPLETED' then 'Delivered'
                    when UPPER(a.latest_order_status) = 'CANCELLED' then 'Cancelled'
                    else 'In Process'
                end as Log_Ondc_Status,
                a.network_retail_order_id,
                a.item_category_id,
                CASE 
                    when a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE a.shipment_type END as shipment_type,
                CASE
                        WHEN REGEXP_LIKE(a.pick_up_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as pick_up_pincode,
                CASE
                        WHEN REGEXP_LIKE(a.delivery_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as delivery_pincode,
                case
                    when a.network_retail_order_category is null then 'Undefined'
                    when a.network_retail_order_category = '' then 'Undefined'
                    else a.network_retail_order_category
                end as network_retail_order_category,
                case 
                    when a.item_tat is null then a.category_tat
                    else a.item_tat
                end as tat,
                a.on_confirm_sync_response,
                a.on_confirm_error_code,
                a.on_confirm_error_message,
                a.rts_tat_duration,
                date_parse(a.rts_tat,'%Y-%m-%dT%H:%i:%s') AS rts_tat,
                a.pickup_tat_duration,
                date_parse(a.pickup_tat,'%Y-%m-%dT%H:%i:%s') as pickup_tat,
                a.motorable_distance ,
                a.motorable_distance_type,
                b."Network order id" as "retail_noi",
                b."Accepted at"
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date a
                LEFT join table2 b ON upper(a.network_retail_order_id) = upper(b."network order id")
                --WHERE date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) >= DATE('2024-05-01')
                except 
                select
                a.bap_id,
                a.bpp_id,
                a.provider_id,
                a.order_id,
                a.fulfillment_id,
                a.transaction_id,
                a.item_id,
                a.fulfillment_status,
                a.fulfillment_type,
                date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s') as order_created_at,
                date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) as "Date",
                a.domain,
                date_parse(a.o_accepted_at_date,'%Y-%m-%dT%H:%i:%s') as o_accepted_at_date,
                date_parse(a.o_in_progress_from_date,'%Y-%m-%dT%H:%i:%s') as o_in_progress_from_date,
                date_parse(a.o_completed_on_date,'%Y-%m-%dT%H:%i:%s') as o_completed_on_date,
                date_parse(a.o_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as o_cancelled_at_date,
                date_parse(a.f_pending_from_date,'%Y-%m-%dT%H:%i:%s') as f_pending_from_date,
                date_parse(a.f_order_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_order_delivered_at_date,
                date_parse(a.f_order_picked_up_date,'%Y-%m-%dT%H:%i:%s') as f_order_picked_up_date,
                date_parse(a.f_out_for_delivery_since_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_delivery_since_date,
                date_parse(a.f_rto_initiated_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_initiated_at_date,
                date_parse(a.f_ready_to_ship_at_date,'%Y-%m-%dT%H:%i:%s') as f_ready_to_ship_at_date,
                CAST(NULLIF(REGEXP_REPLACE(a.cancellation_code, '[^0-9]+', ''), '')AS INTEGER) as cancellation_code,
                date_parse(a.f_cancelled_at_date,'%Y-%m-%dT%H:%i:%s') as f_cancelled_at_date,
                date_parse(a.f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') as f_agent_assigned_at_date,
                date_parse(a.f_out_for_pickup_from_date,'%Y-%m-%dT%H:%i:%s') as f_out_for_pickup_from_date,
                date_parse(a.f_pickup_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_failed_at_date,
                date_parse(a.f_at_destination_hub_from_date,'%Y-%m-%dT%H:%i:%s') as f_at_destination_hub_from_date,
                date_parse(a.f_delivery_failed_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_failed_at_date,
                date_parse(a.f_searching_for_agent_from_date,'%Y-%m-%dT%H:%i:%s') as f_searching_for_agent_from_date,
                date_parse(a.f_pickup_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_pickup_rescheduled_at_date,
                date_parse(a.f_delivery_rescheduled_at_date,'%Y-%m-%dT%H:%i:%s') as f_delivery_rescheduled_at_date,
                date_parse(a.f_in_transit_from_date,'%Y-%m-%dT%H:%i:%s') as f_in_transit_from_date,
                date_parse(a.f_rto_delivered_at_date,'%Y-%m-%dT%H:%i:%s') as f_rto_delivered_at_date,
                date_parse(a."Promised time to deliver",'%Y-%m-%dT%H:%i:%s') as "Promised time to deliver",
                case 
                    when UPPER(a.latest_order_status) = 'COMPLETED' then 'Delivered'
                    when UPPER(a.latest_order_status) = 'CANCELLED' then 'Cancelled'
                    else 'In Process'
                end as Log_Ondc_Status,
                a.network_retail_order_id,
                a.item_category_id,
                CASE 
                    when a.bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE a.shipment_type END as shipment_type,
                CASE
                        WHEN REGEXP_LIKE(a.pick_up_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.pick_up_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END as pick_up_pincode,
                CASE
                        WHEN REGEXP_LIKE(a.delivery_pincode, '[0-9]+') THEN 
                            CASE
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) <= 5 THEN -1
                                WHEN LENGTH(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    )
                                ) > 6 THEN -1
                                ELSE CAST(
                                    COALESCE(
                                        REGEXP_REPLACE(
                                            REGEXP_REPLACE(
                                                REGEXP_REPLACE(a.delivery_pincode, '[^\d]+', ''),  -- Remove non-numeric characters
                                                '\s+', ''  -- Remove spaces
                                            ), 
                                            '^\s|\s$', ''
                                        ), 
                                        NULL
                                    ) AS INTEGER
                                )
                            END
                        ELSE -1
                    END  AS delivery_pincode,
                case
                    when a.network_retail_order_category is null then 'Undefined'
                    when a.network_retail_order_category = '' then 'Undefined'
                    else a.network_retail_order_category
                end as network_retail_order_category,
                case 
                    when a.item_tat is null then a.category_tat
                    else a.item_tat
                end as tat,
                a.on_confirm_sync_response,
                a.on_confirm_error_code,
                a.on_confirm_error_message,
                a.rts_tat_duration,
                date_parse(a.rts_tat,'%Y-%m-%dT%H:%i:%s') AS rts_tat,
                a.pickup_tat_duration,
                date_parse(a.pickup_tat,'%Y-%m-%dT%H:%i:%s') as pickup_tat,
                a.motorable_distance ,
                a.motorable_distance_type,
                b."Network order id" as "retail_noi",
                b."Accepted at"
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date a
                LEFT join table2 b ON upper(a.network_retail_order_id) = upper(b."network order id")
                WHERE date(date_parse(a.order_created_at,'%Y-%m-%dT%H:%i:%s')) >= DATE('2024-05-01')
                AND date_parse(f_agent_assigned_at_date,'%Y-%m-%dT%H:%i:%s') IS NULL
                AND UPPER(latest_order_status) = 'CANCELLED'
                AND (CASE 
                    when bpp_id = 'ondc-lsp.olacabs.com' THEN 'P2P'
                    ELSE shipment_type END) = 'P2P') a WHERE (
                        a.bap_id NOT IN (
                            'ondcpreprodtest.sellerapp.in', 'integrations-preprod.channelier.com', 'ondcpreprod.sellerapp.in', 
                            'preprod-ondc.viranc.com/p/v1/store', 'ondc.testtoprod.production.com', 'biz.test.bitsila.com'
                        ) or a.bap_id is null)
                AND (a.bpp_id NOT IN ('my.ithinklogistics.com/ondc/preprod', 'ondc-preprod-lsp.olacabs.com', 'preprod.ondc.adloggs.com') or a.bpp_id is null)
                AND (a.on_confirm_sync_response <> 'NACK' OR a.on_confirm_sync_response IS NULL)
                AND (a.on_confirm_error_code IS NULL OR a.on_confirm_error_code NOT IN ('65001', '66001'))
                AND cast("Date" as varchar) < '{last_run_date}'
                GROUP BY date_format(date_parse(CAST("Date" as VARCHAR), '%Y-%m-%d'), '%Y-%m')
                ORDER BY month""",

        "B2C_L1_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'fact_order_detail' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count_till_last_run_date,
                count(1) as row_count_till_last_run_date
                from {SCHEMA_SOURCE}.fact_order_detail fod where cast("order_date" as varchar) < '{last_run_date}'
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "B2B_L1_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'fact_order_detail_b2b' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count_till_last_run_date,
                count(1) as row_count_till_last_run_date
                from {SCHEMA_SOURCE}.fact_order_detail_b2b fodbb  where cast("order_date" as varchar) < '{last_run_date}'
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "GV_L1_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L1_query' as dashboard, 'retail_voucher_fact_order_detail' as view_name,
                COUNT(distinct "network_order_id") as distinct_order_count_till_last_run_date,
                count(1) as row_count_till_last_run_date
                from {SCHEMA_SOURCE}.retail_voucher_fact_order_detail fodbb  where cast("order_date" as varchar) < '{last_run_date}'
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "logistics_L1_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
                'Logistics' as sub_domain_name, 'Logistics' as domain_name, 
                'OD_with_L1_query' as dashboard,
                'logistics_fact_order_detail' as view_name,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',
                "bpp_id",'_',CAST("order_date" AS varchar))) as distinct_order_count_till_last_run_date,
                count(1) as row_count_till_last_run_date
                from {SCHEMA_SOURCE}.logistics_fact_order_detail where cast("order_date" as varchar) < '{last_run_date}'
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "B2C_L2_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'district_level_orders' as view_name,
                sum(total_orders_delivered) as distinct_order_count_till_last_run_date,
                count(1) as row_count_till_last_run_date
                from {SCHEMA_SOURCE}.district_level_orders dlo  where cast("order_date" as varchar) < '{last_run_date}'
                group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",
                
        "B2B_L2_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'retail_b2b_district_level_orders' as view_name,
            sum(total_orders_delivered) as distinct_order_count_till_last_run_date,
            count(1) as row_count_till_last_run_date
            from {SCHEMA_SOURCE}.retail_b2b_district_level_orders  where cast("order_date" as varchar) < '{last_run_date}'
            group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "GV_L2_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_with_L2_query' as dashboard, 'retail_voucher_district_level_orders' as view_name,
            sum(total_orders_delivered) as distinct_order_count_till_last_run_date,
            count(1) as row_count_till_last_run_date
            from {SCHEMA_SOURCE}.retail_voucher_district_level_orders rvdlo where cast("order_date" as varchar) < '{last_run_date}'
            group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",
        
        "logistics_L2_query_LRD": f"""select to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date as month, 
            'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_with_L2_query' as dashboard, 'logistics_district_level_orders' as view_name,
            sum(total_orders_delivered) as distinct_order_count_till_last_run_date,
            count(1) as row_count_till_last_run_date
            from {SCHEMA_SOURCE}.logistics_district_level_orders ldlo where cast("order_date" as varchar) < '{last_run_date}'
            group by to_timestamp(cast("order_date" as varchar), 'YYYY-MM')::date""",

        "OD_NO_validation_query_LRD": f"""select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 'B2C' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard, 'shared_order_fulfillment_nhm_fields_view_hudi' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network order id") as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_order_fulfillment_nhm_fields_view_hudi where "o_created date & time" < '{last_run_date}'
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 'B2B' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard,'shared_b2b_order_fullfillment_view' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network order id") as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_b2b_order_fullfillment_view where "o_created date & time" < '{last_run_date}'
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 'Voucher' as sub_domain_name, 'Retail' as domain_name, 'NO_without_base_query' as dashboard,'shared_gift_card_order_fulfillment' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network_order_id") as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_gift_card_order_fulfillment where CAST(o_created_at_date AS VARCHAR) < '{last_run_date}'
                group by date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')
                union
                select date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'NO_without_base_query' as dashboard,'shared_logistics_item_fulfillment_view_with_date' as view_name,
                count(1) as row_count_till_last_run_date,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))) as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_logistics_item_fulfillment_view_with_date where CAST("order_created_at" AS VARCHAR) < '{last_run_date}'
                group by date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 'B2C' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard, 'nhm_order_fulfillment_subset_v1' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network order id") as distinct_order_count_till_last_run_date
                from {DATABASE}.nhm_order_fulfillment_subset_v1 where "o_created date & time" < '{last_run_date}'
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m') as month, 'B2B' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_b2b_order' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network order id") as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_open_data_b2b_order where "o_created date & time" < '{last_run_date}'
                group by date_format(date_parse("o_created date & time" , '%Y-%m-%dT%H:%i:%s'), '%Y-%m')
                union
                select date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 'Voucher' as sub_domain_name, 'Retail' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_gift_voucher_order' as view_name,
                count(1) as row_count_till_last_run_date,
                count(distinct "network order id") as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_open_data_gift_voucher_order where CAST(o_created_at_date AS VARCHAR) < '{last_run_date}'
                group by date_format(date_parse(CAST(o_created_at_date AS VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')
                union
                select date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m') as month, 'Logistics' as sub_domain_name, 'Logistics' as domain_name, 'OD_without_base_query' as dashboard,'shared_open_data_logistics_order' as view_name,
                count(1) as row_count_till_last_run_date,
                COUNT(distinct concat("order_id", '_',"transaction_id",'_',"bap_id",'_',"bpp_id",'_',CAST("order_created_at" AS varchar))) as distinct_order_count_till_last_run_date
                from {DATABASE}.shared_open_data_logistics_order where CAST("order_created_at" as VARCHAR) < '{last_run_date}'
                group by date_format(date_parse(CAST("order_created_at" as VARCHAR), '%Y-%m-%d %H:%i:%s.%f'), '%Y-%m')"""
    }

    return queries