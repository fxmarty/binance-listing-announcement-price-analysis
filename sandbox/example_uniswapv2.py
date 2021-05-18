from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import numpy as np
import datetime

import web3

from lib.tbx_plot_functions import plot_candles
from lib.tbx_data_utils import convert_ohlcv_from_1m_to
from lib.tbx_query_graphql_uniswapv2 import construct_ohlcv_uniform, get_query
from lib.tbx_retrieve_block_time import retrieve_block_from_date

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# on mainnet
w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))


pair_address = "0xbb2b8038a1640196fbe3e38816f3e67cba72d940"

my_date = datetime.datetime(2021, 1, 10, 18, 56)
timestamp = int(my_date.replace(tzinfo=datetime.timezone.utc).timestamp())
num_block = retrieve_block_from_date(timestamp, w3)
print(timestamp)
print(num_block)

res_list = construct_ohlcv_uniform(pair_address, num_block, 20, 'WETH', client, w3)

##
plot_candles(res_list, title="1min", unit="s")

# res_query = get_query(pair_address, 1, block_number, client)

##
# 11628923 - 11628927
res_query = get_query(pair_address, 6, 11628884, client)
