
import logging
import functools

from web3 import Web3

from .. import models as l_models

logger = logging.getLogger("tasks")


def sync_event_start_end_block_number(key, init_start_block_number, interval, rpc_server_address):
    # print(key, init_start_block_number, interval, rpc_server_address)
    def decorator(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            from_block_number = init_start_block_number
            tag = None
            try:
                tag = l_models.Tag.objects.get(key=key)
                last_sync_block_height = int(tag.value)
                from_block_number = last_sync_block_height + 1
            except l_models.Tag.DoesNotExist as exc:
                tag = l_models.Tag.objects.create(key=key, value=str(init_start_block_number))

            to_block_number = from_block_number + interval - 1
            w3 = Web3(Web3.HTTPProvider(rpc_server_address))
            last_block_number = w3.eth.block_number
            if to_block_number > last_block_number:
                to_block_number = last_block_number

            logger.info(f"key: {key} from_block_number: {from_block_number} to_block_number: {to_block_number}")

            kwargs["from_block_number"] = from_block_number
            kwargs["to_block_number"] = to_block_number

            result = func(*args, **kwargs)

            tag.value = str(to_block_number)
            tag.save()

            return result
        return inner
    return decorator


def get_cluster_id(owner, operator_ids):
    cluster_id = Web3.solidity_keccak(["address", "uint64[]"], [owner, operator_ids]).hex()
    return cluster_id
