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
                               since=exchange.parse8601('2020-01-01T00:00:00'),
                               limit=exchange.parse8601('2020-01-01T01:00:00'))
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
import ccxt

def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None

exchanges_list = ccxt.exchanges
exchange_list_currated = ['bitfinex', 'bitfinex2', 'gateio', 'ftx', 'probit',
                          'hitbtc', 'bittrex', 'kucoin', 'okex', 'digifinex',
                          'poloniex', 'yobit', 'stex', 'coinex']

for exchange_name in exchange_list_currated:
    exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})

    print('-----------', exchange_name)

    if not exchange.has['fetchOHLCV']:
        print('No OHLCV.')
        continue

    if exchange.timeframes is not None:
        if '1m' not in exchange.timeframes:
            print('No 1min data available.')
            continue

    try:
        markets = list(exchange.load_markets().keys())
    except Exception as e:
        print(e)

    pairs_checked =('USDT/BTC', 'BTC/USDT', 'USDC/BTC', 'BTC/USDC')
    check_list = [pair in markets for pair in pairs_checked]
    present_pair_index = find_element_in_list(True, check_list)

    if present_pair_index is None:
        print('No common pair found, aborting this exchange.')
        continue
    else:
        pair_name = pairs_checked[present_pair_index]
        print(pair_name)

        try:
            candles = exchange.fetch_ohlcv(pair_name,
                                           timeframe='1m',
                                           since=exchange.parse8601('2020-01-01T00:00:00Z'))
                                           #limit=exchange.parse8601('2020-01-01T01:00:00Z'))
            print(candles[0])
            print(exchange.iso8601(candles[0][0]))
        except Exception as e:
            print('Could not get candles:', e)
