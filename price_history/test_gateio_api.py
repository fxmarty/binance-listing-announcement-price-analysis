import gate_api
import datetime

configuration = gate_api.Configuration(host="https://api.gateio.ws/api/v4")

api_client = gate_api.ApiClient(configuration)
api_instance = gate_api.SpotApi(api_client)

currency_pair = 'BTC_USDT'

date_from = datetime.datetime(2021, 1, 1, 0, 0, 0)
date_from = date_from.replace(tzinfo=datetime.timezone.utc).timestamp()

date_to = datetime.datetime(2021, 1, 1, 1, 0, 0)
date_to = date_to.replace(tzinfo=datetime.timezone.utc).timestamp()

res = api_instance.list_candlesticks(currency_pair,
                                     _from=int(date_from),
                                     to=int(date_to),
                                     interval='1m')
print(res)
