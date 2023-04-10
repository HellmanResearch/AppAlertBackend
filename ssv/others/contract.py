import json

from web3 import Web3

from django.conf import settings


def get_contract():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
    abi = json.loads(settings.SSV_ABI)
    contract = w3.eth.contract(address=settings.SSV_ADDRESS, abi=abi)
    return contract


def get_last_block_number():
    w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
    return w3.eth.block_number
