import ccxt
from lib.tbx_plot_functions import plot_candles
from lib.tbx_data_utils import convert_ohlcv_from_1m_to


if __name__ == '__main__':

    """
    Example of use
    """

    exchange = ccxt.kucoin({'enableRateLimit': True})
    candles = exchange.fetch_ohlcv('BTC/USDT', timeframe='1m', since=exchange.parse8601('2020-01-08T00:00:00'))

    print(candles[0])
    print(exchange.iso8601(candles[0][0]))

    res = convert_ohlcv_from_1m_to('1m', candles)
    plot_candles(res[:150], title="1min", save_path='1min.png', unit="ms")

    res = convert_ohlcv_from_1m_to('5m', candles)
    plot_candles(res[:150], title="5min", index_marker=10, save_path='5min.png',
                 unit="ms")

    res = convert_ohlcv_from_1m_to('15m', candles)
    plot_candles(res, title="15min", save_path='15min.png', unit="ms")
