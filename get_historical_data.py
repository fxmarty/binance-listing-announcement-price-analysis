import ccxt

import pandas as pd

import datetime
import pytz

def check_substring_presence(substring, str_list):
    res = []
    for i, string in enumerate(str_list):
        if substring.upper() in string.upper().split('/'):
            res.append(string)
    return res


def get_market_pairs():
    with open('dat/good_CEX.txt', 'r') as f:
        exchanges = [line.rstrip() for line in f]

    df_listing = pd.read_csv('dat/listings_extracted_manual_edits.csv',
                            converters={'token_names': eval})

    markets_dict = dict()
    for exchange_name in exchanges:
        print(exchange_name)
        exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})
        markets_dict[exchange_name] = list(exchange.load_markets().keys())

    return markets_dict, df_listing


fr_timezone = pytz.timezone("Europe/Paris")
utc_timezone = pytz.timezone("UTC")

markets_dict, df_listing = get_market_pairs()

for index, row in df_listing.iterrows():
    symbol = row['symbols']
    print(symbol)

    time_fr = row['announcement_time']

    year = int(time_fr[:4])
    month = int(time_fr[5:7])
    day = int(time_fr[8:10])
    hour = int(time_fr[11:13])
    minutes = int(time_fr[14:16])

    local_time_formatted = datetime.datetime(year, month, day, hour, minutes)
    local_time_formatted = fr_timezone.localize(local_time_formatted)
    utc_time = local_time_formatted.astimezone(utc_timezone)

    print('Listing time UTC:', utc_time)

    present_in_exchanges = dict()
    for exchange_name in markets_dict:
        represented_pairs = check_substring_presence(symbol, markets_dict[exchange_name])

        exchange = getattr(ccxt, exchange_name)({'enableRateLimit': True})

        valid_represented_pairs = []
        for pair in represented_pairs:

            try:
                candles = exchange.fetch_ohlcv(
                        pair,
                        timeframe='1m',
                        since=exchange.parse8601(utc_time.isoformat()))
            except Exception as e:
                print('Could not get candle:', e)
                continue

            try:
                #print(candles[0])
                #print(exchange.iso8601(candles[0][0]))

                # check the returned time from the exchange corresponds to the
                # listing time on Binance
                cond = exchange.iso8601(candles[0][0])[:13] == utc_time.isoformat()[:13]

                # we have sensible data available
                cond = cond and candles[0][1] != 0 and candles[0][-1] != 0
                if cond:
                    print([exchange.iso8601(candles[0][0])] + candles[0][1:])
                else:
                    continue
                    #print('NOT GOOD:', [exchange.iso8601(candles[0][0])] + candles[0][1:])

            except Exception as e:
                print('Could not print candle (' + exchange_name + '):', e)
                continue

            valid_represented_pairs.append(pair)

        if len(valid_represented_pairs) != 0:
            present_in_exchanges[exchange_name] = valid_represented_pairs

    print(present_in_exchanges)
    print()