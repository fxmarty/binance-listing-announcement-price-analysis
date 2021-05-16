from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import json
import numpy as np

import web3

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# on mainnet
w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))


def get_query(pair_address, number_of_transactions, block_number,
              gql_client):

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
    return client.execute(gql_query)['swaps']


"""
`upper_block_number` block not included
"""
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

# Execute the query on the transport
# result = client.execute(query)


# parsed = json.loads(result)
#print(json.dumps(result, indent=4, sort_keys=True))

address = '0xdfa42ba0130425b21a1568507b084cc246fb0c8f'

result = get_query('0xdfa42ba0130425b21a1568507b084cc246fb0c8f',
                4, 11628864, client)

##
res = construct_ohlcv(address, 11628864 - 30 * 20, 11628864, 30, 'USDC',
                      client, w3)

##
from lib.tbx_plot_functions import plot_candles

##
plot_candles(res, title="Hehe", unit="s")