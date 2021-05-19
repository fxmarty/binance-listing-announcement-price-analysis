import web3

import datetime

import json

##

# on goerli testnet
# w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

# on mainnet
w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

wei_to_eth = 1e-18

res = w3.eth.get_block(6440727)

##
print(w3.isConnected())
##
with open('./DEX/example_abi.abi', 'r') as f:
    abi = f.readlines()

abi = json.loads(abi[0])

##
contract = w3.eth.contract('0xB4FBF271143F4FBf7B91A5ded31805e42b2208d6', abi=abi)

##
my_account = w3.eth.account.create('Nobody expects the Spanish Inquisition!')

nonce = w3.eth.getTransactionCount(my_account.address)

##

# uniswap approve example
transaction = contract.functions.approve(my_account.address, 10)

transaction = transaction.buildTransaction({'nonce': nonce})

signed_tx = w3.eth.account.sign_transaction(transaction, my_account.privateKey)
#gas = signed_tx.estimateGas()

txn_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)


## get block
# block = w3.eth.get_block(5000000)

my_date = datetime.datetime(2018, 1, 30, 14, 44, 33)
my_timestamp = int(datetime.datetime.timestamp(my_date))

n_closest = retrieve_block_from_date(my_timestamp, w3)

##
# Now, how to get Uniswap contract address for the pair ABC/ETH
# given the token address for ABC?

transac = w3.eth.get_transaction('0x55701b70e3221a2c48428ea1321f584dec466a9e1bdc6ae737ef87a7b7856b3a')

## pair contract on mainnet, check its address
with open('./DEX/uniswap_v2_factory.abi', 'r') as f:
    abi = f.readlines()

abi = json.loads(abi[0])

contract = w3.eth.contract('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', abi=abi)

#get pair contract address from two tokens
address1 = w3.toChecksumAddress('0x7206579d60e985928098ea8ff8773c66788a9cdc')

# wETH contract address
address2 = w3.toChecksumAddress('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
print(contract.functions.getPair(address1, address2).call())

## Test with BSC
from web3.middleware import geth_poa_middleware

w3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print(w3.isConnected())

res = w3.eth.get_block(6440727)

##
with open('./sandbox/DEX/pancakeswap_v2_factory.abi', 'r') as f:
    abi = f.readlines()

abi = json.loads(abi[0])

# PancakeSwap v2 Factory contract
contract = w3.eth.contract('0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', abi=abi)

# VAI address
address1 = w3.toChecksumAddress('0x4BD17003473389A42DAF6a0a729f6Fdb328BbBd7')

# BUSD address
address2 = w3.toChecksumAddress('0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56')

print(contract.functions.getPair(address1, address2).call())
