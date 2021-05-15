from web3 import Web3

import datetime

import json

# on goerli testnet
# w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

# on mainnet
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

wei_to_eth = 1e-18

##
print(w3.isConnected())
##
with open('/home/felix/Documents/Projets/binance-listing-announcement-price-analysis/DEX/example_abi.abi', 'r') as f:
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
"""
This function returns the closest ** next ** block number from a date given
in the timestamp format.
"""
def retrieve_block_from_date(timestamp, w3):
    cur_min = 0
    cur_max = w3.eth.get_block_number()  # get most recent block number

    if w3.eth.get_block(cur_min).timestamp > timestamp:
        raise ValueError("The requested time is too old.")

    if w3.eth.get_block(cur_max).timestamp < timestamp:
        raise ValueError("The requested time is in the future...")

    current_closest_block_number = cur_max

    n_it = 0
    while True:
        n_it += 1
        print(n_it, "---", cur_min, "--", cur_max)
        previous_block_num = cur_max
        next_block_num = cur_min + (cur_max - cur_min) // 2

        if cur_max - cur_min <= 1:
            break

        previous_block_num = next_block_num

        if w3.eth.get_block(next_block_num).timestamp > timestamp:
            cur_max = next_block_num
        else:
            cur_min = next_block_num

    return cur_max  # return the upper one

##

# block = w3.eth.get_block(5000000)

my_date = datetime.datetime(2018, 1, 30, 14, 44, 33)
my_timestamp = int(datetime.datetime.timestamp(my_date))

n_closest = retrieve_block_from_date(my_timestamp, w3)

##
# Now, how to get Uniswap contract address for the pair ABC/ETH
# given the token address for ABC?

transac = w3.eth.get_transaction('0x55701b70e3221a2c48428ea1321f584dec466a9e1bdc6ae737ef87a7b7856b3a')

##
input_length = len('0xc9c65396') \
               + 2*len('000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
token_address_length = len('000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')

##

with open('/home/felix/Documents/Projets/binance-listing-announcement-price-analysis/DEX/uniswap_v2_factory.abi', 'r') as f:
    abi = f.readlines()

abi = json.loads(abi[0])

contract = w3.eth.contract('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', abi=abi)


##
address1 = w3.toChecksumAddress('0x7206579d60e985928098ea8ff8773c66788a9cdc')

# wETH contract address
address2 = w3.toChecksumAddress('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')
print(contract.functions.getPair(address1, address2).call())