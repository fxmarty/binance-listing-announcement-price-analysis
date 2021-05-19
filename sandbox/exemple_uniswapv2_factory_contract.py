"""
Exemple of call to UniSwap's v2 factory contract to retrieve a pair contract
address from the address of the two underlying tokenss
"""


import web3
import json

if __name__ == "__main__":
    # on mainnet
    w3 = web3.Web3(web3.Web3.HTTPProvider('https://mainnet.infura.io/v3/2087d99dcbd0422496ac13960fae645d'))

    with open('./sandbox/DEX/uniswap_v2_factory.abi', 'r') as f:
        abi = f.readlines()

    abi = json.loads(abi[0])

    # uniSwap v2 Factory contract
    contract = w3.eth.contract('0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f', abi=abi)

    weth_address = w3.toChecksumAddress("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")

    # USDC ERC-20
    address_token2 = w3.toChecksumAddress("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

    print(contract.functions.getPair(weth_address, address_token2).call())
