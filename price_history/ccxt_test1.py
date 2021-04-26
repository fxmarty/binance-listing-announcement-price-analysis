import ccxt
exchange = ccxt.kucoin({ 'enableRateLimit': True })
candles = exchange.fetch_ohlcv('BTC/USDT',
                               timeframe='1m',
                               since=exchange.parse8601('2020-01-08T00:00:00'))
#print(exchange.has['fetchOHLCV'])
print(candles[0])
print(exchange.iso8601(candles[0][0]))
##
#print(ccxt.exchanges)

exchange = ccxt.binance({ 'enableRateLimit': True })

candles = exchange.fetch_ohlcv('BTC/USDT',
                               timeframe='1m',
                               since=exchange.parse8601('2020-01-07T03:20:00+00:00'),
                               limit=exchange.parse8601('2020-01-07T04:20:00+00:00'))
print(candles[0])
print(exchange.iso8601(candles[0][0]))

##
exchange = ccxt.kraken({ 'enableRateLimit': True })

markets = exchange.load_markets()


##
exchange = ccxt.aax({ 'enableRateLimit': True })

candles = exchange.fetch_ohlcv('BTC/USDT',
                               timeframe='1d',
                               since=exchange.parse8601('2021-01-01T00:00:00'),
                               limit=exchange.parse8601('2021-01-04T01:00:00'))
print(candles[0])
print(exchange.iso8601(candles[0][0]))

##
