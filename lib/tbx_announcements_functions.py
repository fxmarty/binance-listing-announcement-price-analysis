import re
import time
from pycoingecko import CoinGeckoAPI
from lib.tbx_data_utils import check_presence


def get_identification_from_symbol(symbol, list_of_dict):
    """
    TODO: add function description
    """

    res = []
    for token in list_of_dict:
        if token["symbol"].lower() == symbol.lower():
            res.append(token)
    return res


def get_information_from_announcement(soup, title, announcement_time, cg_tokens):
    """
    TODO: add function description
    """

    listing_time = None
    symbols = list(set(re.findall("(?<=\()[A-Z0-9]*(?=\))", title)))

    symbols_last_words = dict()

    if len(symbols) != 0:
        for symbol in symbols:
            regex = ".+(?=\s\(" + symbol + "\))"
            regex_search = re.search(regex, title)
            symbols_last_words[symbol] = regex_search.group().split(" ")[-4:]

    token_names = []

    # Used to retrieve contract address
    cg = CoinGeckoAPI()
    bep20_contract = []
    erc20_contract = []
    bep2_contract = []

    date = int(announcement_time[:4] + announcement_time[5:7] + announcement_time[8:10])

    # From the 04/08/2020 on, Binance changed its template for announcements
    # and also uses span instead of div for articles' content
    if date >= 20200804:
        article = soup.find_all("article")
    else:
        article = soup.find_all("div", {"class": "css-nleihe"})

    # Iterate over all paragraphs
    for paragraphs in article:
        elements = paragraphs.find_all(["div", "span"])

        possible_contracts = paragraphs.find_all("a", {"href": True})

        for possible_contract in possible_contracts:
            href = possible_contract.attrs["href"]
            contract = href.rsplit("/", 1)[-1].lower()
            if "etherscan.io" in href and contract not in erc20_contract:
                erc20_contract.append(contract)
            elif "bscscan.com" in href and contract not in bep20_contract:
                bep20_contract.append(contract)
            elif "explorer.binance.org" in href and contract not in bep2_contract:
                bep2_contract.append(contract)

        res = ""
        for i in range(len(elements)):
            res = res + elements[i].text
        paragraph = res

        if len(symbols) == 0:
            symbols = list(set(re.findall("(?<=\()[A-Z0-9]*(?=\))", paragraph)))

            for symbol in symbols:
                regex = ".+(?=\s\(" + symbol + "\))"
                regex_search = re.search(regex, paragraph)
                symbols_last_words[symbol] = regex_search.group().split(" ")[-4:]

        if listing_time is None:
            # Consider announce and listing year to be the same
            year = announcement_time[:4]
            listing_time = re.search(year + ".*?\(UTC\)", paragraph)
            if listing_time is not None:
                listing_time = listing_time.group()

    if "UTC" in symbols:
        symbols.remove("UTC")

    # Use coingecko to retrieve the token name, as well as contract addresses
    # if they are not already given in the listing page
    for symbol in symbols:
        list_coingecko_identification = get_identification_from_symbol(symbol.lower(), cg_tokens)

        # Found on coingecko several tokens with the same symbol, pass additional
        # test later to select the good one(s)
        if len(list_coingecko_identification) > 1:
            pass_filtering_test = True
        else:
            pass_filtering_test = False

        for coingecko_token_identification in list_coingecko_identification:
            coingecko_token_id = coingecko_token_identification["id"]
            coingecko_token_name = coingecko_token_identification["name"]

            cg_name_last_words = coingecko_token_name.split(" ")[-4:]

            filtered_condition = True

            if pass_filtering_test:
                filtered_condition = check_presence(cg_name_last_words, symbols_last_words[symbol])

            if filtered_condition:
                token_names.append(coingecko_token_name)

                # we need to handle the query limit in coingecko (<100/min)
                passed = False
                info_token = None
                while not passed:
                    try:
                        info_token = cg.get_coin_by_id(coingecko_token_id)
                    except Exception:
                        print("Sleeping 5 seconds to calm down coingecko...")
                        time.sleep(5)
                    if info_token is not None:
                        passed = True

                for site in info_token["links"]["blockchain_site"]:
                    if site is None:
                        continue
                    if not site.startswith("http"):
                        continue

                    contract = site.rsplit("/", 1)[-1].lower()
                    if "etherscan.io" in site:
                        if all(contract != contract_in for contract_in in erc20_contract):
                            erc20_contract.append(contract)
                    elif "bscscan.com" in site:
                        if all(contract != contract_in for contract_in in bep20_contract):
                            bep20_contract.append(contract)
                    elif "explorer.binance.org" in site:
                        if all(contract != contract_in for contract_in in bep2_contract):
                            bep2_contract.append(contract)

    return (listing_time, symbols, token_names, bep20_contract, erc20_contract, bep2_contract)
