import ccxt
import numpy as np
import pandas as pd


def check_presence(list1_str, list2_str):
    """
    Returns `True` if at least one element of `list1_str`
    is in `list2_str`
    """

    intersection = [value for value in list1_str if value in list2_str]

    return len(intersection) != 0


def convert_ohlcv_from_1m_to(precision, data_list):
    """
    This function converts OHLCV data fetched with a 1 minute granularity to higher ones
    """

    n_aggregate = -1
    if precision == "1m":
        return data_list
    elif precision == "5m":
        n_aggregate = 5
    elif precision == "15m":
        n_aggregate = 15
    elif precision == "30m":
        n_aggregate = 30
    else:
        raise ValueError("Conversion not supported.")

    res = []
    current_min = np.inf
    current_max = -np.inf
    current_open = -1
    current_close = -1
    current_time = -1
    current_volume = 0

    length_result = len(data_list) // n_aggregate

    for i in range(length_result):
        current_time = data_list[i * n_aggregate][0]

        buffer = np.array(data_list[i * n_aggregate:(i + 1) * n_aggregate])

        # np.where returns a tuple
        buffer2 = np.where(np.isnan(buffer[:, 1]) == False)[0]

        if len(buffer2) == 0:
            current_open = np.nan
        else:
            current_open = buffer[buffer2[0], 1]

        # np.where returns a tuple
        buffer2 = np.where(np.isnan(buffer[:, 4]) == False)[0]

        if len(buffer2) == 0:
            current_close = np.nan
        else:
            current_close = buffer[buffer2[-1], 4]

        if np.isnan(current_open):
            current_min = np.nan
            current_max = np.nan
        else: # at least one swap happened
            for j in range(n_aggregate):
                current_min = min(current_min, data_list[i * n_aggregate + j][3])
                current_max = max(current_max, data_list[i * n_aggregate + j][2])
                current_volume += data_list[i * n_aggregate + j][5]


        res.append([current_time, current_open, current_max,
                    current_min, current_close, current_volume])

        current_min = np.inf
        current_max = -np.inf
        current_open = -1
        current_close = -1
        current_time = -1
        current_volume = 0

    return res


def find_element_in_list(element, list_element):
    """
    Returns the index of an element in a list if it is present,
    but returns `None` otherwise
    """

    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None


def get_market_pairs():
    """
    Returns a dictionary s.t. its keys are exchanges names, and pairs
    lists of pairs available on the corresponding exchange.
    """

    with open("dat/good_CEX.txt", "r") as f:
        exchanges = [line.rstrip() for line in f]

    markets_dict = dict()
    for exchange_name in exchanges:
        print(exchange_name)
        exchange = getattr(ccxt, exchange_name)({"enableRateLimit": True})
        markets_dict[exchange_name] = list(exchange.load_markets().keys())

    return markets_dict


def check_substring_presence(substring, str_list):
    """
    This function checks a symbol `substring` (e.g. 'ABC') in a list of pairs,
    for example str_list = ['ABC/USD', 'BTC/USD', 'USD/EUR', 'EUR/ABC'].

    In this example returns ['ABC/USD', 'EUR/ABC'].
    """

    res = []
    for string in str_list:
        if substring.upper() in string.upper().split("/"):
            res.append(string)
    return res


def filter_out_nontrading(input_list):
    """
    In a OHLCV dataset given as a list, removes rows with 0 volume.

    This is useful for mplfinance to not plot non-trading intervals.
    """
    res = []
    for row in input_list:
        if row[5] != 0:
            res.append(row)
    return res


def next_non_nan(index, data):
    """
    Get the next non_nan index for a given index in an OHLCV list,
    where the outputs consider that the NaN rows will be removed

    Sets index to None if no non-NaN row is found
    """

    n = len(data)
    n_nan = 0
    res_index = None
    for i in range(n):
        if data[i][5] == 0:
            n_nan += 1

        if data[i][5] > 0 and i >= index:
            res_index = i - n_nan
            break

    return res_index