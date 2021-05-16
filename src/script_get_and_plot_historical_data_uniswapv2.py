import os
import ccxt
import pytz
import datetime

import pandas as pd

from lib.tbx_data_utils import get_market_pairs


if __name__ == "__main__":

    fr_timezone = pytz.timezone("Europe/Paris")
    utc_timezone = pytz.timezone("UTC")

    df_listing = pd.read_csv("dat/listings_extracted_manual_edits_blocks.csv",
                             converters={"token_names": eval})

    for index, row in df_listing.iterrows():
        # this is not a ERC-20 token, skip it
        if row["ethereum_block_number"] == -1:
            continue

        symbol = row["symbols"]
        print(symbol)

        time_fr = row["announcement_time"]

        year = int(time_fr[:4])
        month = int(time_fr[5:7])
        day = int(time_fr[8:10])
        hour = int(time_fr[11:13])
        minutes = int(time_fr[14:16])

        local_time_formatted = datetime.datetime(year, month, day, hour, minutes)
        local_time_formatted = fr_timezone.localize(local_time_formatted)
        utc_time = local_time_formatted.astimezone(utc_timezone)

        dir_path = os.path.join("dat/listings_data", utc_time.strftime("%Y-%m-%dT%H:%MZ") + "_" + symbol)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        print("Listing time UTC:", utc_time)

        next_block = row["ethereum_block_number"]

