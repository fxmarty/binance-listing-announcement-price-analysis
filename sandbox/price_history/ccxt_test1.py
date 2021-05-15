import ccxt
exchange = ccxt.kucoin({ 'enableRateLimit': True })
candles = exchange.fetch_ohlcv('BTC/USDT',
                               timeframe='1m',
                               since=exchange.parse8601('2020-01-08T00:00:00'))
#print(exchange.has['fetchOHLCV'])
print(candles[0])
print(exchange.iso8601(candles[0][0]))

##
candles_array = np.array(candles)

index_df = pd.DataFrame({'Date': candles_array[:, 0].astype(int)})
index_df['Date'] = pd.to_datetime(index_df['Date'], unit='ms')


##
dataset = pd.DataFrame({'Open': candles_array[:, 1],
                        'High': candles_array[:, 2],
                        'Low': candles_array[:, 3],
                        'Close': candles_array[:, 4],
                        'Volume': candles_array[:, 5]},
                       index=pd.DatetimeIndex(index_df['Date']))

dataset.index.name = 'Date'

##

save_params = dict(fname='/home/felix/saved_file_candles.jpg',
                   dpi=300, bbox_inches='tight')
mpf.plot(dataset[:500], type='candle', volume=True, show_nontrading=True,
         style='charles', savefig=save_params)
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
