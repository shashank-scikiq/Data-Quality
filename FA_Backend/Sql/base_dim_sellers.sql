select
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) AS order_date,
	"seller np name" AS seller_np
from "ATH_DB"."BASE_TABLE"
where date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) = Date('{date_val}')
group by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name"
order by date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')), "seller np name";