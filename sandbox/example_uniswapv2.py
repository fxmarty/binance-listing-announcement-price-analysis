from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import numpy as np
import datetime

import web3

from lib.tbx_plot_functions import plot_candles
from lib.tbx_data_utils import convert_ohlcv_from_1m_to
from lib.tbx_query_graphql_uniswapv2 import construct_ohlcv_uniform, get_query
from lib.tbx_retrieve_block_time import retrieve_block_from_date


if __name__ == "__main__":
    # Select your transport with a defined url endpoint
    thegraph_address = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    transport = AIOHTTPTransport(url=thegraph_address)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # on mainnet
    infura_address = "https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d"
    w3 = web3.Web3(web3.Web3.HTTPProvider(infura_address))

    # WETH/WBTC pair
    pair_address = "0xbb2b8038a1640196fbe3e38816f3e67cba72d940"

    my_date = datetime.datetime(2021, 1, 10, 18, 56)
    timestamp = int(my_date.replace(tzinfo=datetime.timezone.utc).timestamp())
    num_block = retrieve_block_from_date(timestamp, w3)

    res_list = construct_ohlcv_uniform(pair_address, num_block, n_minutes=30,
                                       reference_symbol="WETH",
                                       gql_client=client, w3=w3)

    plot_candles(res_list, title="1min", unit="s", plot_type="candle",
                 show_nontrading=False, fill_between=True)

    # res_list = np.load('1min.npy').tolist()