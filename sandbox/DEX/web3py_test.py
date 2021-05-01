from web3 import Web3

import json

# on goerli testnet
w3 = Web3(Web3.HTTPProvider('https://goerli.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

wei_to_eth = 1e-18

##
print(w3.isConnected())
##
with open('contract_ex_sol_IUniswapV2Pair.abi', 'r') as f:
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

