import json
import logging
import subprocess

from web3 import Web3
from web3.datastructures import AttributeDict

from .. import models as l_models
import eth_abi
from django.db import IntegrityError
from django.conf import settings
import web3
from eth_abi import codec

from . import utils as l_utils

logger = logging.getLogger("tasks")


def save_cluster(event):
    args = event["args"]
    # cluster_id = encode_packed(["address", "uint64[]"], [args["owner"], args["operatorIds"]]).hex()
    # cluster_id = Web3.solidity_keccak(["address", "uint64[]"], [args["owner"], args["operatorIds"]]).hex()
    cluster_id = l_utils.get_cluster_id(args["owner"], args["operatorIds"])
    operator_ids = [str(item) for item in args["operatorIds"]]
    operator_ids_str = ",".join(operator_ids)
    balance_human = args["cluster"]["balance"] / 1e18

    try:
        l_models.Cluster.objects.create(
            id=cluster_id,
            owner=args["owner"],
            operator_ids=operator_ids_str,
            balance_human=balance_human,
        )
    except IntegrityError:
        pass


# def get_cluster_est_days(cluster: l_models.Cluster,
#                          network_fee,
#                          network_fee_index,
#                          cluster_network_fee_index,
#                          cluster_validator_count,
#                          cluster_index,
#                          minimum_blocks_before_liquidation,
#                          minimum_liquidation_collateral):
#     expand = 10000000
#     cluster_balance_now = int(cluster.balance_human * 1e18)
#     operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
#     operator_list = [l_models.Operator.objects.get(id=operator_id) for operator_id in operator_ids]
#
#     operator_fee_sum = sum([operator.fee_human * 38264 for operator in operator_list])
#     operator_fee_sum_expand = operator_fee_sum * expand
#
#     minimum_liquidation_collateral_expand = minimum_liquidation_collateral * expand
#
#     liquidation_threshold_expand = minimum_blocks_before_liquidation * (
#             operator_fee_sum_expand + network_fee) * cluster_validator_count
#
#     liquidation_threshold_amount = max(liquidation_threshold_expand, minimum_liquidation_collateral_expand)
#
#     print("liquidation_threshold_expand: ", liquidation_threshold_expand)
#
#     block_per_day = 7200
#     network_burn_per_day = network_fee * block_per_day * cluster_validator_count
#     operator_burn_per_day = operator_fee_sum * block_per_day * cluster_validator_count
#
#     available_balance = cluster_balance_now - liquidation_threshold_amount
#
#     est_days = available_balance / ((network_burn_per_day + operator_burn_per_day) * expand)
#     est_days = max(0, est_days)
#     return est_days


def update_cluster_balance_est_days(cluster,
                                    contract,
                                    network_fee,
                                    minimum_blocks_before_liquidation,
                                    minimum_liquidation_collateral):
    # owner = '0xFEa21ef0edB800EDCc7B8f576A3EbA1847436970'
    # operator_ids = [314, 315, 316, 317]
    # cluster_info2 = {'validatorCount': 1, 'networkFeeIndex': 0, 'index': 7538008, 'active': True,
    #                  'balance': 9000000000000000000}
    # r = contract.functions.getBalance(owner, operator_ids, cluster_info2).call()

    owner = Web3.to_checksum_address(cluster.owner)
    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    cluster_info = {
        "validatorCount": cluster.validator_count,
        "networkFeeIndex": cluster.network_fee_index,
        "index": cluster.index,
        "active": cluster.active,
        "balance": int(cluster.balance),
    }

    balance = contract.functions.getBalance(owner,
                                            operator_ids,
                                            cluster_info
                                            ).call()
    # cluster.balance = balance
    cluster.balance_human = balance / 1e18
    cluster.save()

    try:
        est_days = get_cluster_est_days2(cluster=cluster,
                                         network_fee=network_fee,
                                         minimum_blocks_before_liquidation=minimum_blocks_before_liquidation,
                                         minimum_liquidation_collateral=minimum_liquidation_collateral)
        cluster.est_days = est_days
        cluster.save()
    except Exception as exc:
        logger.warning(f"get_cluster_est_days cluster_id: {cluster.id} error: {exc}")


def get_cluster_est_days2(cluster: l_models.Cluster,
                          network_fee,
                          minimum_blocks_before_liquidation,
                          minimum_liquidation_collateral):

    expand = 1e7
    block_per_day = 7200

    cluster_balance = int(cluster.balance_human * 1e18)

    if cluster_balance <= minimum_liquidation_collateral:
        return 0

    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    operator_list = [l_models.Operator.objects.get(id=operator_id) for operator_id in operator_ids]
    operator_fee_sum = sum(item.fee_human for item in operator_list)
    operator_fee_sum_per_block = operator_fee_sum * 1e18 / (7200 * 365)

    network_fee_per_block = network_fee

    liquidation_amount = (operator_fee_sum_per_block + network_fee_per_block) * minimum_blocks_before_liquidation

    max_liquidation_amount = max(liquidation_amount, minimum_liquidation_collateral)

    if cluster_balance < max_liquidation_amount:
        return 0

    cost_per_day = (operator_fee_sum_per_block + network_fee_per_block) * block_per_day * cluster.validator_count

    if cost_per_day == 0:
        return 999999999

    est_operational_runway = (cluster_balance - max_liquidation_amount) / cost_per_day
    return est_operational_runway


def process_cluster(formatted_log, update_keys={}):
    # args = formatted_log["args"]
    # operator_id_str = ",".join(args["operatorIds"])
    # owner = args["owner"].lower()
    #
    # cluster_info =
    # print("formatted_log: ", formatted_log)
    args = formatted_log["args"]
    operator_id_list = [str(item) for item in args["operatorIds"]]
    operator_id_str = ",".join(operator_id_list)
    # owner = args["owner"].lower()
    owner = args["owner"]
    cluster_info = args["cluster"]

    cluster_id = l_utils.get_cluster_id(args["owner"], args["operatorIds"])

    cluster, is_new = l_models.Cluster.objects.get_or_create(id=cluster_id, owner=owner, operator_ids=operator_id_str)
    cluster.active = cluster_info["active"]
    cluster.balance = str(cluster_info["balance"])
    cluster.balance_human = cluster_info["balance"] / 1e18
    cluster.index = cluster_info["index"]
    cluster.network_fee_index = cluster_info["networkFeeIndex"]
    cluster.validator_count = cluster_info["validatorCount"]

    for key, value in update_keys.items():
        setattr(cluster, key, value)

    cluster.save()


def process_log(contract, log):

    event_name_list = ["ValidatorAdded", "ValidatorRemoved", "ClusterLiquidated", "ClusterReactivated",
                       "ClusterWithdrawn", "ClusterDeposited"]
    topic_map = {getattr(contract.events, event_name).create_filter(fromBlock=0).builder.topics[0]: event_name for
                 event_name in event_name_list}

    log_topic_0_hex = log["topics"][0].hex()
    event_name = topic_map.get(log_topic_0_hex)
    if event_name is None:
        return
    formatted_log = getattr(contract.events, event_name).create_filter(fromBlock=0).format_entry(log)
    update_keys = {}
    if event_name == "ClusterLiquidated":
        update_keys["liquidated"] = True
    process_cluster(formatted_log, update_keys)
    return

    # if log_topic_0_hex == contract.events.ValidatorAdded.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ValidatorAdded.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log)
    #
    # elif log_topic_0_hex == contract.events.ValidatorRemoved.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ValidatorRemoved.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log)
    #
    # elif log_topic_0_hex == contract.events.ClusterLiquidated.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ClusterLiquidated.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log, update_keys={"liquidated": True})
    #
    # elif log_topic_0_hex == contract.events.ClusterReactivated.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ClusterReactivated.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log)
    #
    # elif log_topic_0_hex == contract.events.ClusterWithdrawn.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ClusterWithdrawn.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log)
    #
    # elif log_topic_0_hex == contract.events.ClusterDeposited.create_filter(fromBlock=0).builder.topics[0]:
    #     formatted_log = contract.events.ClusterDeposited.create_filter(fromBlock=0).format_entry(log)
    #     process_cluster(formatted_log)


# def update_cluster2(cluster, contract):
#     from_block = max(cluster.last_sync_block_number, settings.SSV_INIT_HEIGHT)
#     owner_topic = "0x" + eth_abi.encode(["address"], [cluster.owner]).hex()
#     # filter_params = {
#     #     "address": settings.SSV_ADDRESS,
#     #     "fromBlock": from_block,
#     #     "toBlock": from_block + 10000,
#     #     "topics": [None, owner_topic]
#     #     # "topics": ["0x48a3ea0796746043948f6341d17ff8200937b99262a0b48c2663b951ed7114e5"]
#     # }
#
#     filter_params = {
#         "address": settings.SSV_ADDRESS,
#         "fromBlock": 18508041,
#         "toBlock": 18510858,
#         # "topics": ["0x48a3ea0796746043948f6341d17ff8200937b99262a0b48c2663b951ed7114e5"]
#     }
#     w3 = Web3(Web3.HTTPProvider(settings.ETH_URL))
#     log_list = w3.eth.get_logs(filter_params)
#     for log in log_list:
#         process_log(contract, log)
#     pass

def update_cluster2(cluster, contract):
    pass
