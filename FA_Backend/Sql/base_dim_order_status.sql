select
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) order_date,
	"seller np name" AS seller_np,
	"Order Status" AS order_status,
	"Cancellation code" AS cancellation_code
from ATH_DB.BASE_TABLE
where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) = Date('{date_val}')
group by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name",
	"Order Status",
	"Cancellation code"
order by "seller np name";