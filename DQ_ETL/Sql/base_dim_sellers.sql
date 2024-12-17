select
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')) AS order_date,
	"seller np name" AS seller_np
from "ATH_DB"."BASE_TABLE"
where extract(month from date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s'))) = extract(month from date('{date_val}'))
group by
	date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')),
	"seller np name"
order by date(date_parse("O_Created Date & Time", '%Y-%m-%dT%H:%i:%s')), "seller np name";