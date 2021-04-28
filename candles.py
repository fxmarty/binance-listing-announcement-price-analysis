import mplfinance as mpf
import numpy as np
import pandas as pd


# convert OHLCV data fetched with a 1 minute granularity to higher ones
def convert_ohlcv_from_1m_to(precision, data_list):
    n_aggregate = -1
    if precision == '1m':
        return data_list
    elif precision == '5m':
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


# wrapper method to either plot on the fly candles' graph or save it
def plot_candles(candles_list, title='', save_path=None, index_marker=None):
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


    plots_list = []
    if index_marker:
        signal = [np.nan] * len(candles_list)
        signal[index_marker] = candles_list[index_marker][3]  # low
        apd = mpf.make_addplot(signal, type='scatter', markersize=30, marker='^', alpha=0.5)
        plots_list.append(apd)

    if save_path is not None:
        save_params = dict(fname=save_path,
                        dpi=300, bbox_inches='tight')
        mpf.plot(dataset, type='candle', volume=True, show_nontrading=True,
                style='charles', title=title, addplot=plots_list, savefig=save_params)
    else:
        mpf.plot(dataset, type='candle', volume=True, show_nontrading=True,
                style='charles', title=title, addplot=plots_list)

# example of use
if __name__ == '__main__':
    import ccxt
    exchange = ccxt.kucoin({ 'enableRateLimit': True })
    candles = exchange.fetch_ohlcv('BTC/USDT',
                                   timeframe='1m',
                                   since=exchange.parse8601('2020-01-08T00:00:00'))
    print(candles[0])
    print(exchange.iso8601(candles[0][0]))

    res = convert_ohlcv_from_1m_to('1m', candles)
    plot_candles(res[:150], title="1min", save_path='1min.png')

    res = convert_ohlcv_from_1m_to('5m', candles)
    plot_candles(res[:150], title="5min", index_marker=10, save_path='5min.png')

    res = convert_ohlcv_from_1m_to('15m', candles)
    plot_candles(res, title="15min", save_path='15min.png')