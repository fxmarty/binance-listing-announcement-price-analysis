# import this package
from poloniex import Poloniex

# make an instance of poloniex.Poloniex
polo = Poloniex()

ticker = polo('returnTicker')


##

# using a 'helper' method
print(polo.returnChartData(currencyPair='BTC_LTC', period=900))
# bypassing 'helper'
print(polo(command='returnChartData', args={'currencyPair': 'BTC_LTC',
                                            'period': 900}))

print(polo.marketTradeHist('BTC_ETH'))
