# coding: utf-8
import requests

# see https://www.okex.com/docs/en/#spot-line

host = "https://www.okex.com/api/spot/v3"
#headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

url = '/instruments/BTC-USDT/candles?granularity=300&start=2021-04-25T16:00:00.000Z&end=2021-04-25T17:00:00.000Z'
query_param = ''
r = requests.request('GET', host + url) #, headers=headers)
print(r.json())
