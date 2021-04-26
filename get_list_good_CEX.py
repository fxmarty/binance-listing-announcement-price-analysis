import ccxt

def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None

exchanges_list = ccxt.exchanges

# a smaller list, whose exchanges have high volume and are well known, as well
# as havng a decent number of pairs compared to Binance
exchange_list_currated = ['bitfinex', 'bitfinex2', 'gateio', 'ftx', 'probit',
                          'hitbtc', 'bittrex', 'kucoin', 'okex', 'digifinex',
                          'poloniex', 'yobit', 'stex', 'coinex', 'bithumb',
                          'latoken', 'bitmart', 'ascendex', 'upbit', 'hbtc', 'vcc',
                          'bitforex', 'bitz']

exchange_allow_1m_history = []

'''
Result:

['bitfinex',
 'bitfinex2',
 'probit',
 'hitbtc',
 'bittrex',
 'kucoin',
 'ascendex',
 'upbit',
 'vcc']

allow 1min history in 2020.

# exclude upbit which is Korean exchange.
# exclude bitfinex2 which is the v2 API of Bitfinex
'''

for exchange_name in exchange_list_currated:
    exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})

    print('-----------', exchange_name)

    if not exchange.has['fetchOHLCV']:
        print('No OHLCV.')
        continue

    #print(exchange.timeframes)
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
            candles = exchange.fetch_ohlcv(
                            pair_name,
                            timeframe='1m',
                            since=exchange.parse8601('2020-01-01T00:00:00Z'))
                            #limit=exchange.parse8601('2020-01-01T01:00:00Z'))
            print(candles[0])
            date_iso = exchange.iso8601(candles[0][0])
            print(date_iso)

            if date_iso.startswith('2020-01-01'):
                exchange_allow_1m_history.append(exchange_name)

        except Exception as e:
            print('Could not get candles:', e)

with open('dat/good_CEX.txt', 'w') as f:
    for exchange in exchange_allow_1m_history:
        f.write(exchange)
        f.write('\n')