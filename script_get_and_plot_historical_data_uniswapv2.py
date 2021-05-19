import os
import ccxt
import pytz
import datetime
import warnings

import pandas as pd
import json

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

import web3

from lib.tbx_plot_functions import plot_candles
from lib.tbx_data_utils import convert_ohlcv_from_1m_to
from lib.tbx_query_graphql_uniswapv2 import construct_ohlcv_uniform
from lib.tbx_retrieve_block_time import retrieve_block_from_date


if __name__ == "__main__":

    fr_timezone = pytz.timezone("Europe/Paris")
    utc_timezone = pytz.timezone("UTC")

    df_listing = pd.read_csv("./dat/listings_extracted_manual_edits_blocks.csv",
                             converters={"token_names": eval,
                                         "erc20_contract": eval})

    exchange_name = "uniswapv2"

    # on mainnet
    w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

    # Select your transport with a defined url endpoint
    thegraph_address = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    transport = AIOHTTPTransport(url=thegraph_address)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    with open('./sandbox/DEX/uniswap_v2_factory.abi', 'r') as f:
        abi = f.readlines()

    abi = json.loads(abi[0])

    # PancakeSwap v2 Factory contract
    contract = w3.eth.contract('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', abi=abi)

    weth_address = w3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    for index, row in df_listing.iterrows():
        # this is not a ERC-20 token, skip it
        if row["ethereum_block_number"] == -1 or row["erc20_contract"] == []:
            continue

        if len(row["erc20_contract"]) > 1:
            raise ValueError(f"`erc20_contract` list larger than 1, something is"
                             f" wrong with the token {row['symbols']}.")

        symbol = row["symbols"]
        print("---", symbol, "---")

        time_fr = row["announcement_time"]

        year = int(time_fr[:4])
        month = int(time_fr[5:7])
        day = int(time_fr[8:10])
        hour = int(time_fr[11:13])
        minutes = int(time_fr[14:16])

        local_time_formatted = datetime.datetime(year, month, day, hour, minutes)
        local_time_formatted = fr_timezone.localize(local_time_formatted)
        utc_time = local_time_formatted.astimezone(utc_timezone)

        # We look ahead 20 minutes for context
        utc_time_shifted = utc_time - datetime.timedelta(hours=0, minutes=20)

        dir_path = os.path.join("./dat/listings_data",
                                utc_time.strftime("%Y-%m-%dT%H:%MZ") + "_" + symbol)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        print("Listing time UTC:", utc_time)

        timestamp_utc_time_shifted = int(
            utc_time_shifted.replace(tzinfo=datetime.timezone.utc).timestamp())
        starting_block = retrieve_block_from_date(timestamp_utc_time_shifted, w3)

        token_address = w3.toChecksumAddress(row["erc20_contract"][0])

        pair_address = contract.functions.getPair(weth_address,
                                                  token_address).call()

        if pair_address == "0x0000000000000000000000000000000000000000":
            warnings.warn(f"Uniswap's factory could not retrieve the pair address"
                          f" for WETH/{symbol}. Maybe the token {token_address} is"
                          f" not listed yet on UniSwap?",
                          stacklevel=2)
            continue

        candles = construct_ohlcv_uniform(pair_address, starting_block,
                                          n_minutes=120,
                                          reference_symbol="WETH",
                                          gql_client=client, w3=w3)
        if candles == []:
            continue

        pair_formatted = f"WETH - {symbol}"
        file_name = exchange_name + "_" + pair_formatted + "_1m"
        file_path = os.path.join(dir_path, file_name + ".png")

        plot_candles(candles, title=file_name, index_marker=20,
                     save_path=file_path, unit="s",
                     show_nontrading=False, fill_between=True)

        res = convert_ohlcv_from_1m_to("5m", candles)
        file_name = exchange_name + "_" + pair_formatted + "_5m"
        file_path = os.path.join(dir_path, file_name + ".png")
        plot_candles(res, title=file_name, index_marker=4,
                     save_path=file_path, unit="s",
                     show_nontrading=False, fill_between=True)
