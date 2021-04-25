import os
import time
import pandas as pd
from bs4 import BeautifulSoup

import re


def get_infos(soup):
    # Get the full article
    article = soup.find_all("article")

    listing_time = None
    symbols = None

    # Iterate over all paragraphs
    for paragraphs in article:
        symbols = []
        paragraphs = paragraphs.find_all("div")
        for paragraph in paragraphs:
            paragraph = paragraph.text

            # Split the paragraphs into sentences and iterate over it
            for sentence in paragraph.split("."):

                # Tokenize the sentence into a list of words
                words = sentence.replace(
                    ".", "").replace(",", "").split(" ")

                # If the sentence does not contain "(UTC)" we pass
                if "(UTC)" in words:

                    # Oterwise get the index of the word "(UTC)"
                    indices = [i for i, e in enumerate(
                        words) if e == "(UTC)"]
                    if len(indices) == 1:
                        i = indices[0]
                        if words[i-1] in ["AM", "PM"]:
                            hour = words[i-3]
                            minute = words[i-2]
                            am_pm = words[i-1]
                            listing_time = "{} {} {}".format(hour, minute, am_pm)
                            j_max = i-3
                        else:
                            hour = words[i-2]
                            minute = words[i-1]
                            listing_time = "{} {}".format(hour, minute)
                            j_max = i-2

                        for j in range(0, j_max):

                            if len(words[j]) > 0:
                                if words[j][0] == "(" and words[j][-1] == ")":
                                    symbol = words[j][1:-1]
                                    symbols.append(symbol)
                                elif "/" in words[j]:
                                    symbol = words[j]
                                    symbols.append(symbol)
    return listing_time, symbols



if __name__ == "__main__":

    annoucements_base_path = "dat/annoucement_pages/"
    all_announcements = sorted(os.listdir(annoucements_base_path))

    df_col = ["announcement", "likely_listing", "title", "announcement_time", "listing_time",
              "symbols", "token_names"]
    df = pd.DataFrame(columns=df_col)

    announcement_positive_flags = ['launchpool',
                                   'launchpad',
                                   'binance will list',
                                   'binance lists',
                                   'innovation zone']

    # exclusive flags
    announcement_negative_flags = ['leveraged token',
                                   'stock token',
                                   'binance completes',
                                   'stable coin',
                                   'wrapped']

    # those are symbols we do NOT want in crypto names
    banned_symbols = ['BTC', 'USD']


    for annoucement in all_announcements:
        if not annoucement.endswith('.html'):
            continue

        with open(os.path.join(annoucements_base_path, annoucement)) as fp:

            soup = BeautifulSoup(fp, 'html.parser')

            # Get the title of the article
            title = soup.find_all("div", {"class": "css-kxziuu"})
            assert len(title) == 1
            title = title[0].text

            # Get the announcement time, i.e., YYYY-MM-DD hh:mm
            announcement_time = soup.find_all("div", {"class": "css-17s7mnd"})
            assert len(announcement_time) == 1
            announcement_time = announcement_time[0].text

            likely_listing_announcement = False

            if any(flag in title.lower() for flag in announcement_positive_flags):
                likely_listing_announcement = True

            if any(flag in title.lower() for flag in announcement_negative_flags):
                likely_listing_announcement = False

            listing_time = ""
            symbols = ""
            if likely_listing_announcement:
                listing_time, symbols = get_infos(soup)

        print(annoucement)

        # perform the analysis from 01-01-2020 only
        if not announcement_time.startswith(('2021', '2020')):
            break

        line = pd.DataFrame({"announcement": [annoucement],
                             "likely_listing": [likely_listing_announcement],
                             "title": [title],
                             "announcement_time": [announcement_time],
                             "listing_time": [listing_time],
                             "symbols": [symbols],
                             "token_names": [""]}
                            )
        print(title)
        print()
        df = df.append(line)

    df.to_csv("dat/symbols_extracted.csv")
