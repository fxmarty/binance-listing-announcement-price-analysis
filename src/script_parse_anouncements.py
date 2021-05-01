import re
import os
import time
import pandas as pd
from bs4 import BeautifulSoup
from pycoingecko import CoinGeckoAPI
from lib.tbx_data_utils import check_presence
from lib.tbx_announcements_functions import get_information_from_announcement


if __name__ == "__main__":

    annoucements_base_path = "dat/annoucement_pages/"

    # We reverse the order to discard any announcement of a previously listed symbol, was e.g. a problem with SafePal token
    all_announcements = sorted(os.listdir(annoucements_base_path), reverse=True)

    all_symbols = []
    duplicates = []

    df_col = [
        "announcement",
        "title",
        "announcement_time",
        "symbols",
        "token_names",
        "bep20_contract",
        "erc20_contract",
        "bep2_contract",
    ]
    df_listings = pd.DataFrame(columns=df_col)
    df_non_listings = pd.DataFrame(columns=df_col)

    # Define flags
    announcement_positive_flags = ["launchpool", "launchpad", "binance will list", "binance lists", "innovation zone"]
    announcement_negative_flags = ["leveraged token", "stock token", "binance completes", "stable coin", "wrapped"]

    # Those are symbols we do NOT want in crypto names, as they are likely pegged to other assets
    banned_symbols = ["btc", "usd"]

    cg = CoinGeckoAPI()
    cg_tokens = cg.get_coins_list()

    for annoucement in all_announcements:
        if not annoucement.endswith(".html"):
            continue

        with open(os.path.join(annoucements_base_path, annoucement)) as fp:

            soup = BeautifulSoup(fp, "html.parser")

            # Get the title of the article
            title = soup.find_all("div", {"class": "css-kxziuu"})
            assert len(title) == 1
            title = title[0].text

            # Get the announcement time, i.e., YYYY-MM-DD hh:mm
            announcement_time = soup.find_all("div", {"class": "css-17s7mnd"})
            assert len(announcement_time) == 1
            announcement_time = announcement_time[0].text

            # Perform the analysis from 01-01-2020 only
            if not announcement_time.startswith(("2021", "2020")):
                continue

            likely_listing_announcement = False

            if any(flag in title.lower() for flag in announcement_positive_flags):
                likely_listing_announcement = True

            if any(flag in title.lower() for flag in announcement_negative_flags):
                likely_listing_announcement = False

            # Look for banned symbols between parenthesis
            for symbol in banned_symbols:
                matches = re.findall("\([a-z]*" + symbol + "[a-z]*\)", title.lower())
                if len(matches) != 0:
                    likely_listing_announcement = False

            print(annoucement)
            print(title)

            listing_time = ""
            symbols = []
            token_names = []
            bep20_contract = []
            erc20_contract = []
            bep2_contract = []
            if likely_listing_announcement:
                listing_time, symbols, token_names,
                bep20_contract, erc20_contract,
                bep2_contract = get_information_from_announcement(soup, title, announcement_time, cg_tokens)

        # Skip this assert, but it will need to be checked manually
        # assert len(symbols) == len(token_names)

        # We will handle the case where the symbol has not been detected
        if len(symbols) != 0:
            for i, symbol in enumerate(symbols):
                line = pd.DataFrame(
                    {
                        "announcement": [annoucement],
                        "title": [title],
                        "announcement_time": [announcement_time],
                        "symbols": [symbol],
                        "token_names": [token_names],
                        "bep20_contract": [bep20_contract],
                        "erc20_contract": [erc20_contract],
                        "bep2_contract": [bep2_contract],
                    }
                )

                # The symbol has already been seen, likely a false positive
                if not check_presence([symbol], all_symbols):
                    all_symbols.append(symbol)
                else:
                    likely_listing_announcement = False
                    duplicates.append(symbol)

                if likely_listing_announcement:
                    df_listings = df_listings.append(line)
                else:
                    df_non_listings = df_non_listings.append(line)
        else:
            line = pd.DataFrame(
                {
                    "announcement": [annoucement],
                    "title": [title],
                    "announcement_time": [announcement_time],
                    "symbols": [symbols],
                    "token_names": [token_names],
                    "bep20_contract": [bep20_contract],
                    "erc20_contract": [erc20_contract],
                    "bep2_contract": [bep2_contract],
                }
            )

            # The symbol has already been seen, likely a false positive
            if not check_presence(symbols, all_symbols):
                all_symbols.extend(symbols)
            else:
                likely_listing_announcement = False
                duplicates.extend(symbols)

            if likely_listing_announcement:
                df_listings = df_listings.append(line)
            else:
                df_non_listings = df_non_listings.append(line)

    print("Discarded duplicates:", duplicates)

    # Go back in the sorted order
    df_listings = df_listings[::-1]
    df_non_listings = df_non_listings[::-1]

    df_listings.to_csv("dat/listings_extracted.csv", index=False)
    df_non_listings.to_csv("dat/non_listings_extracted.csv", index=False)
