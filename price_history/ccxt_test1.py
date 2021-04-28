import ccxt
exchange = ccxt.kucoin({ 'enableRateLimit': True })
candles = exchange.fetch_ohlcv('BTC/USDT',
                               timeframe='1m',
                               since=exchange.parse8601('2020-01-08T00:00:00'))
#print(exchange.has['fetchOHLCV'])
print(candles[0])
print(exchange.iso8601(candles[0][0]))

##
import mplfinance as mpf
import numpy as np
import pandas as pd

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

##


def convert_ohlcv_from_1m_to(precision, data_list):
    n_aggregate = -1
    if precision == '5m':
        n_aggregate = 5
    elif precision == '15m':
        n_aggregate = 15
    elif precision == '30m':
        n_aggregate = 30
    else:
        raise ValueError('Conversion not supported.')

    res = []
    current_min = np.inf
    current_max = - np.inf
    current_open = -1
    current_close = -1
    current_time = -1
    current_volume = 0

    length_result = len(data_list) // n_aggregate

    for i in range(length_result):
        current_time = data_list[i * n_aggregate][0]
        current_open = data_list[i * n_aggregate][1]
        for j in range(n_aggregate):
            current_min = min(current_min,
                              data_list[i * n_aggregate + j][3])
            current_max = max(current_max,
                              data_list[i * n_aggregate + j][4])
            current_volume += data_list[i * n_aggregate + j][5]
        current_close = data_list[i * n_aggregate + (n_aggregate - 1)][2]

        res.append([current_time, current_open, current_max,
                    current_min, current_close, current_volume])

        current_min = np.inf
        current_max = - np.inf
        current_open = -1
        current_close = -1
        current_time = -1
        current_volume = 0

    return res
##
def plot_candles(candles_list):
    candles_array = np.array(candles_list)

    index_df = pd.DataFrame({'Date': candles_array[:, 0].astype(int)})
    index_df['Date'] = pd.to_datetime(index_df['Date'], unit='ms')

    dataset = pd.DataFrame({'Open': candles_array[:, 1],
                            'High': candles_array[:, 2],
                            'Low': candles_array[:, 3],
                            'Close': candles_array[:, 4],
                            'Volume': candles_array[:, 5]},
                        index=pd.DatetimeIndex(index_df['Date']))

    dataset.index.name = 'Date'

    save_params = dict(fname='/home/felix/saved_file_candles.jpg',
                    dpi=300, bbox_inches='tight')
    mpf.plot(dataset, type='candle', volume=True, show_nontrading=True,
            style='charles') #, savefig=save_params)

##
res = convert_ohlcv_from_1m_to('5m', candles_array)

##
plot_candles(candles_array)
##
plot_candles(res)
