from gql import gql, Client

import numpy as np
import asyncio
import warnings

import web3

from lib.tbx_retrieve_block_time import retrieve_block_from_date


def get_query(pair_address, number_of_transactions, block_number,
              gql_client):
    """
    Retrieve a query about swaps for e.g. UniSwap (given with `gql_client`),
    where `number_of_transactions` transactions are retrieved for the contract
    with the address `pair_address`, **before** and including the block `block_number`.
    """

    pair_address = pair_address.lower()  # The Graph expects lower addresses

    # double brackets to escape { and } in the f-string
    query_string = f"""
query trades{{
    swaps(where:{{pair: "{pair_address}"}},
                orderBy: timestamp,
                orderDirection: desc,
                first:{number_of_transactions},
                block: {{number:{block_number} }}) {{
        id
        timestamp
        amount0In
        amount1In
        amount0Out
        amount1Out
        pair {{
            token0 {{
                id
                symbol
            }}
            token1 {{
                id
                symbol
            }}
        }}
        transaction {{
            blockNumber
        }}
    }}
}}
"""
    gql_query = gql(query_string)

    while True:
        try:
            result = gql_client.execute(gql_query)['swaps']
            break
        except gql.transport.exceptions.TransportQueryError:
            print("gql.transport.exceptions.TransportQueryError,"
                  " calling again `execute`...")
    return result


""" ***** probably to delete, but let's see *****
`upper_block_number` block not included
def construct_ohlcv(pair_address, block_number, upper_block_number,
                    grouping_number, reference_symbol, gql_client, w3):

    assert (upper_block_number - block_number) % grouping_number == 0

    res = []
    n_done = 0
    n_todo = (upper_block_number - block_number) // grouping_number

    result = get_query(pair_address, 1, block_number, gql_client)

    # we need to determine which token is our reference token, e.g. for volume
    if result[0]["pair"]["token0"]["symbol"] == reference_symbol:
        ref_index = 0
        sec_index = 1
    else:
        sec_index = 0
        ref_index = 1

    # will hold the swap amounts
    total = [-1, -1]

    for i in range(n_todo - 1, -1, -1):
        timestamp = w3.eth.get_block(
                        upper_block_number - (n_todo - i) * grouping_number)["timestamp"]
        current_min = np.inf
        current_max = -np.inf
        current_open = np.nan
        current_close = np.nan
        current_volume = 0

        n_block_current = upper_block_number - (n_todo - i - 1) * grouping_number
        last_swap = True
        first_swap = False
        last_id = ""
        stop = False

        while True:
            # need to check that current_block is not the same as previously...
            result = get_query(pair_address, 100, n_block_current, gql_client)

            for j, swap in enumerate(result):
                if (int(swap["transaction"]["blockNumber"])
                        >= block_number + i * grouping_number):
                    print(swap)

                    # we need this in case we need to call `get_query` several times,
                    # as there may be more than 100 swaps in `grouping_number` blocks.
                    # As we call `get_query` with the last block seen, it could be
                    # that there are duplicates.
                    if last_id == swap["id"]:
                        continue

                    # we don't care about which the direction the swap is made
                    total[ref_index] = (float(swap[f"amount{ref_index}In"])
                                        + float(swap[f"amount{ref_index}Out"]))
                    total[sec_index] = (float(swap[f"amount{sec_index}In"])
                                        + float(swap[f"amount{sec_index}Out"]))

                    current_volume += total[ref_index]
                    rate = total[ref_index] / total[sec_index]

                    current_min = min(current_min, rate)
                    current_max = max(current_max, rate)

                    # always assured that the last writeup will be the open
                    current_open = rate

                    if last_swap:
                        current_close = rate
                        last_swap = False
                else:
                    # we went up to the last swap without going enough back
                    # in time, go further starting from the new `n_block_current`
                    if j == 99:
                        n_old_block = n_block_current
                        n_block_current = int(swap["transaction"]["blockNumber"])

                        if n_old_block == n_block_current:
                            raise ValueError("More than 100 swaps were included" \
                                             " in the same block, we will fall" \
                                             " into an infinite loop.")
                    else:
                        stop = True
                        break

            if stop is True:
                if current_volume == 0:
                    current_max = np.nan
                    current_min = np.nan

                current_res = [timestamp, current_open, current_max,
                               current_min, current_close, current_volume]

                res.insert(0, current_res)
                break

    return res
"""

# expect `block_number` to be the first of a given minute (ideally)
def construct_ohlcv_uniform(pair_address, block_number, n_minutes,
                            reference_symbol, gql_client, w3):
    res = []
    n_done = 0

    while True:
        try:
            result = get_query(pair_address, 1, block_number, gql_client)
            break
        except asyncio.TimeoutError:
            print("asyncio.TimeoutError, calling again `get_query`...")

    if len(result) == 0:
        warnings.warn(f"Querying The Graph for the pair address {pair_address}"
                      f" from block {block_number} did not yield any result. "
                      f"Are you sure the provided inputs to "
                      f"`construct_ohlcv_uniform` are correct or that the pair"
                      f" was already listed at the requested block?",
                      stacklevel=2)
        return []

    # we need to determine which token is our reference token, e.g. for volume
    if result[0]["pair"]["token0"]["symbol"] == reference_symbol:
        ref_index = 0
        sec_index = 1
    elif result[0]["pair"]["token1"]["symbol"] == reference_symbol:
        sec_index = 0
        ref_index = 1
    else:
        raise ValueError(f"Reference symbol indicated to be {reference_symbol}, "
                         f"but pair symbols are {result[0]['pair']['token0']['symbol']}"
                         f" and {result[0]['pair']['token1']['symbol']}.")

    # will hold the swap amounts
    total = [-1, -1]

    limit_blocks = [block_number - 1]
    timestamp_start = w3.eth.get_block(block_number)["timestamp"]
    timestamp_start = timestamp_start - timestamp_start % 60  # start at a round minute
    print("Computing block numbers delimiting minutes...")
    for i in range(1, n_minutes + 1):
        limit_block = retrieve_block_from_date(timestamp_start + 60 * i, w3,
                                               limit_down=limit_blocks[-1] - 1,
                                               limit_up=limit_blocks[-1] + 100)
        print("Minute", i, f" (block {limit_block})...")
        limit_blocks.append(limit_block)

    for i in range(n_minutes - 1, -1, -1):
        print(f'Processing minute {i}...')
        timestamp = timestamp_start + i * 60
        current_min = np.inf
        current_max = -np.inf
        current_open = np.nan
        current_close = np.nan
        current_volume = 0

        last_swap = True
        first_swap = False
        last_id = ""
        stop = False

        n_queries = 10  # number of swaps queried with The Graph

        # last block in the current minute. If there is no block in the current minute,
        # the check with `limit_blocks[i]` prevents to write crap data
        n_block_current = limit_blocks[i + 1] - 1

        while True:
            while True:
                try:
                    # need to check that current_block is not the same as previously...
                    result = get_query(pair_address, n_queries, n_block_current, gql_client)
                    break
                except asyncio.TimeoutError:
                    print("asyncio.TimeoutError, calling again `get_query`...")

            if len(result) == 0:
                stop = True

            for j, swap in enumerate(result):
                if (int(swap["transaction"]["blockNumber"])
                        > limit_blocks[i]):
                    # print(swap)

                    """
                    # we need this in case we need to call `get_query` several times,
                    # as there may be more than 100 swaps in `grouping_number` blocks.
                    # As we call `get_query` with the last block seen, it could be
                    # that there are duplicates.
                    if last_id == swap["id"]:
                        continue
                    """

                    # we don't care about which the direction the swap is made
                    total[ref_index] = (float(swap[f"amount{ref_index}In"])
                                        + float(swap[f"amount{ref_index}Out"]))
                    total[sec_index] = (float(swap[f"amount{sec_index}In"])
                                        + float(swap[f"amount{sec_index}Out"]))

                    current_volume += total[ref_index]
                    rate = total[ref_index] / total[sec_index]

                    current_min = min(current_min, rate)
                    current_max = max(current_max, rate)

                    # always assured that the last writeup will be the open
                    current_open = rate

                    if last_swap:
                        current_close = rate
                        last_swap = False
                else:
                    stop = True
                    break

            if stop is False:
                # we went up to the last swap without going enough back
                # in time, go further starting from the new `n_block_current`
                n_old_block = n_block_current
                n_block_current = int(swap["transaction"]["blockNumber"])

                if n_old_block == n_block_current:
                    # to avoid getting trapped in an infinite loop
                    n_queries += 10

            if stop is True:
                if current_volume == 0:
                    current_max = np.nan
                    current_min = np.nan

                current_res = [timestamp, current_open, current_max,
                               current_min, current_close, current_volume]

                res.insert(0, current_res)
                break

    return res
