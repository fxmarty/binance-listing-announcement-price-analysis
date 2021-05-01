import re

#txt = "Binance Will List sUSD (SUSD) in the Innovation (rrUSDe) Zone".upper()
txt = "Binance Will List Keep3rV1 (KP3R) in the Innovation Zone".upper()
x = re.findall("(?<=\()[A-Z0-9]*(?=\))", txt)

print(x)

##

paragraph = 'hehe 2020/08/17 8:00 AM (UTC). We will then open trading for OCEAN/USDT at 2020/08/19 8:00 AM (UTC)'
year = '2020'
listing_time = re.search(year + ".*?\(UTC\)", paragraph)

if listing_time is not None:
    print(listing_time.group())


##

html_str = '<p><span style="font-weight: 400;">Binance will list </span><span style="font-weight: 400;">FIO Protocol (FIO)</span><span style="font-weight: 400;"> and open trading for </span><span style="font-weight: 400;">FIO/BNB, FIO/BTC and FIO/BUSD</span><span style="font-weight: 400;"> trading pairs at </span>'

from bs4 import BeautifulSoup

soup = BeautifulSoup(html_str, 'html')

elements = soup.find_all("span")

res = ''
for i in range(len(elements)):
    res = res + elements[i].text

##
paragraphs = '<li class="css-usuhj8"><a href="https://etherscan.io/token/0xef3a930e1ffffacd2fc13434ac81bd278b0ecc8d" class="css-li4l4s"><span class="css-1f5vusx">Stafi (FIS) ERC20 Contract Address</span></a></li>'

soup = BeautifulSoup(paragraphs, 'html')

possible_contracts = soup.find_all('a', {'href': True})

##
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

tokens = cg.get_coins_list()

def get_identification_from_symbol(symbol, list_of_dict):
    res = []
    for token in list_of_dict:
        if token['symbol'].lower() == symbol.lower():
            res.append(token)
    return res

#res = get_identification_from_symbol('BIFI', tokens)['id']
print(get_identification_from_symbol('BOT', tokens))

##
info_token = cg.get_coin_by_id(res)

print(info_token['asset_platform_id'])
print(info_token['contract_address'])
print(info_token['platforms'])
print(info_token['links']['blockchain_site'])
#print(cg.get_coin_by_id(res))

##

phrase = 'we will list Compound (COMP) hehehe'
symbol = 'COMP'
regex = ".+(?=\s\(" + symbol + "\))"
print(regex)
print(list(set(re.findall(regex, phrase))))