import numpy as np
import pandas as pd

import pytz
import datetime

from web3 import Web3
from web3.middleware import geth_poa_middleware

from lib.tbx_retrieve_block_time import retrieve_block_from_date


if __name__ == "__main__":
    # on mainnet
    w3_ethereum = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

    # BSC relies of PoA, which seem to require this last line below
    w3_bsc = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
    w3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

    df_listing = pd.read_csv("dat/listings_extracted_manual_edits.csv",
                             converters={"token_names": eval})

    n_columns = df_listing.shape[1]

    column_index = n_columns  # add a new column the dataframe

    df_listing["ethereum_block_number"] = -1
    df_listing["bsc_block_number"] = -1

    fr_timezone = pytz.timezone("Europe/Paris")
    utc_timezone = pytz.timezone("UTC")


    for index, row in df_listing.iterrows():
        print(row["symbols"])
        time_fr = row["announcement_time"]

        year = int(time_fr[:4])
        month = int(time_fr[5:7])
        day = int(time_fr[8:10])
        hour = int(time_fr[11:13])
        minutes = int(time_fr[14:16])

        local_time_formatted = datetime.datetime(year, month, day, hour, minutes)
        local_time_formatted = fr_timezone.localize(local_time_formatted)
        utc_time = local_time_formatted.astimezone(utc_timezone)

        utc_timestamp = int(utc_time.timestamp())

        if row["erc20_contract"] != "[]":
            closest_block = retrieve_block_from_date(utc_timestamp, w3_ethereum)
            df_listing.loc[index, "ethereum_block_number"] = closest_block
        if row["bep20_contract"] != "[]":
            closest_block = retrieve_block_from_date(utc_timestamp, w3_bsc)
            df_listing.loc[index, "bsc_block_number"] = closest_block

    df_listing.to_csv("dat/listings_extracted_manual_edits_blocks.csv", index=False)
