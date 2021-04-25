import os
import time
import pandas as pd
from bs4 import BeautifulSoup

import re

from pycoingecko import CoinGeckoAPI

def get_infos(soup, title, announcement_time, cg_tokens):
    listing_time = None
    symbols = list(set(re.findall("(?<=\()[A-Z0-9]*(?=\))", title)))

    symbols_last_words = dict()

    if len(symbols) != 0:
        for symbol in symbols:
            regex = ".+(?=\s\(" + symbol + "\))"
            regex_search = re.search(regex, title)
            symbols_last_words[symbol] = regex_search.group().split(' ')[-4:]

    token_names = []
    '''
    token_names = []
    for symbol in symbols:
        regex = "[A-Za-z0-9]+(?=\s\(" + symbol + "\))"
        token_names.extend(list(set(re.findall(regex, title))))
    '''

    cg = CoinGeckoAPI()  # used to retrieve contract address
    bep20_contract = []
    erc20_contract = []
    bep2_contract = []

    date = int(announcement_time[:4] + announcement_time[5:7]
                + announcement_time[8:10])

    # on the 04/08/2020 onward, Binance changed its template for announcements
    # and also uses span instead of div for articles' content
    if date >= 20200804:
        article = soup.find_all("article")
    else:
        article = soup.find_all('div', {'class': 'css-nleihe'})

    # Iterate over all paragraphs
    #print(article)
    for paragraphs in article:
        elements = paragraphs.find_all(["div", 'span'])

        possible_contracts = paragraphs.find_all('a', {'href': True})

        for possible_contract in possible_contracts:
            href = possible_contract.attrs['href']
            contract = href.rsplit('/', 1)[-1].lower()
            if 'etherscan.io' in href and contract not in erc20_contract:
                erc20_contract.append(contract)
            elif 'bscscan.com' in href and contract not in bep20_contract:
                bep20_contract.append(contract)
            elif 'explorer.binance.org' in href and contract not in bep2_contract:
                bep2_contract.append(contract)

        res = ''
        for i in range(len(elements)):
            res = res + elements[i].text
        paragraph = res

        if len(symbols) == 0:
            symbols = list(set(re.findall("(?<=\()[A-Z0-9]*(?=\))", paragraph)))

            for symbol in symbols:
                regex = ".+(?=\s\(" + symbol + "\))"
                regex_search = re.search(regex, paragraph)
                symbols_last_words[symbol] = regex_search.group().split(' ')[-4:]

        if listing_time is None:
            # consider announce and listing year to be the same
            year = announcement_time[:4]
            listing_time = re.search(year + ".*?\(UTC\)", paragraph)
            if listing_time is not None:
                listing_time = listing_time.group()

    if 'UTC' in symbols:
        symbols.remove('UTC')

    # use coingecko to retrieve the token name, as well as contract addresses
    # if they are not already given in the listing page
    for symbol in symbols:
        list_coingecko_identification = get_identification_from_symbol(symbol.lower(),
                                                                       cg_tokens)

        # found on coingecko several tokens with the same symbol, pass additional
        # test later to select the good one(s)
        if len(list_coingecko_identification) > 1:
            pass_filtering_test = True
        else:
            pass_filtering_test = False

        for coingecko_token_identification in list_coingecko_identification:
            coingecko_token_id = coingecko_token_identification['id']
            coingecko_token_name = coingecko_token_identification['name']

            cg_name_last_words = coingecko_token_name.split(' ')[-4:]

            filtered_condition = True

            if pass_filtering_test:
                filtered_condition = check_presence(cg_name_last_words,
                                                    symbols_last_words[symbol])

            if filtered_condition:
                token_names.append(coingecko_token_name)

                # we need to handle the query limit in coingecko (<100/min)
                passed = False
                info_token = None
                while not passed:
                    try:
                        info_token = cg.get_coin_by_id(coingecko_token_id)
                    except Exception:
                        print('Sleeping 5 seconds to calm down coingecko...')
                        time.sleep(5)
                    if info_token is not None:
                        passed = True

                for site in info_token['links']['blockchain_site']:
                    if site is None:
                        continue
                    if not site.startswith('http'):
                        continue

                    contract = site.rsplit('/', 1)[-1].lower()
                    if 'etherscan.io' in site:
                        if all(contract != contract_in for contract_in in erc20_contract):
                            erc20_contract.append(contract)
                    elif 'bscscan.com' in site:
                        if all(contract != contract_in for contract_in in bep20_contract):
                            bep20_contract.append(contract)
                    elif 'explorer.binance.org' in site:
                        if all(contract != contract_in for contract_in in bep2_contract):
                            bep2_contract.append(contract)

    return (listing_time, symbols, token_names,
            bep20_contract, erc20_contract, bep2_contract)


def find_element_in_list(element, list_element):
    try:
        index_element = list_element.index(element)
        return index_element
    except ValueError:
        return None


def get_identification_from_symbol(symbol, list_of_dict):
    res = []
    for token in list_of_dict:
        if token['symbol'].lower() == symbol.lower():
            res.append(token)
    return res

# check that at least one string of `list1_str` is in `list2_str`
def check_presence(list1_str, list2_str):
    res = False

    for elem in list1_str:
        if elem in list2_str:
            res = True
            break
    return res


if __name__ == "__main__":

    annoucements_base_path = "dat/annoucement_pages/"
    all_announcements = sorted(os.listdir(annoucements_base_path))

    df_col = ["announcement", "title", "announcement_time",
              "symbols", "token_names",
              "bep20_contract", "erc20_contract", 'bep2_contract']
    df_listings = pd.DataFrame(columns=df_col)
    df_non_listings = pd.DataFrame(columns=df_col)

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

    # those are symbols we do NOT want in crypto names, as they are likely
    # pegged to other assets
    banned_symbols = ['btc', 'usd']

    cg = CoinGeckoAPI()
    cg_tokens = cg.get_coins_list()

    #for annoucement in all_announcements[370:385]:
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

            # look for banned symbols between parenthesis
            for symbol in banned_symbols:
                matches = re.findall("\([a-z]*" + symbol + "[a-z]*\)", title.lower())
                if len(matches) != 0:
                    likely_listing_announcement = False

            print(annoucement)
            print(title)

            listing_time = ''
            symbols = []
            token_names = []
            bep20_contract = []
            erc20_contract = []
            bep2_contract = []
            if likely_listing_announcement:
                (listing_time, symbols, token_names,
                 bep20_contract, erc20_contract,
                 bep2_contract) = get_infos(soup, title, announcement_time, cg_tokens)

        # perform the analysis from 01-01-2020 only
        if not announcement_time.startswith(('2021', '2020')):
            break

        line = pd.DataFrame({"announcement": [annoucement],
                             "title": [title],
                             "announcement_time": [announcement_time],
                             "symbols": [symbols],
                             "token_names": [token_names],
                             "bep20_contract": [bep20_contract],
                             "erc20_contract": [erc20_contract],
                             "bep2_contract": [bep2_contract]}
                            )
        if likely_listing_announcement:
            df_listings = df_listings.append(line)
        else:
            df_non_listings = df_non_listings.append(line)

        print()

    df_listings.to_csv("dat/listings_extracted.csv")
    df_non_listings.to_csv("dat/non_listings_extracted.csv")
