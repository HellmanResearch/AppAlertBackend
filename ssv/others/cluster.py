import logging
import subprocess

from web3 import Web3
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
    # cmd = f"cd {settings.SSV_CLUSTER_SCANNER};yarn cli -n {settings.ETH_URL} -ca {settings.SSV_ADDRESS} -oa {cluster.owner} -oids {cluster.operator_ids}"
    # logger.info(f"cmd: {cmd}")
    # timeout = 20
    # try:
    #     cp = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    #                         timeout=timeout)
    # except subprocess.TimeoutExpired as exc:
    #     raise TimeoutError(f"timeout ({timeout}s)")
    # if cp.returncode != 0:
    #     raise Exception(f"run cmd failed cp.returncode: {cp.returncode} cp.stdout: {cp.stdout} cp.stderr: {cp.stderr}")
    # try:
    #     cluster_validator_count = int(cp.stdout.split('"validatorCount": "')[1].split('"')[0])
    #     cluster_network_fee_index = int(cp.stdout.split('"networkFeeIndex": "')[1].split('"')[0])
    #     cluster_index = int(cp.stdout.split('"index": "')[1].split('"')[0])
    #     cluster_balance = int(cp.stdout.split('"balance": "')[1].split('"')[0])
    #     cluster_active = cp.stdout.split('"active": ')[1].split('\n')[0]
    #     cluster_active = True if cluster_active == "true" else False
    # except Exception as exc:
    #     raise Exception(f"parse stdout error: {exc}")
    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    balance = contract.functions.getBalance(cluster.owner,
                                            operator_ids,
                                            [
                                                cluster.cluster_validator_count,
                                                cluster.cluster_network_fee_index,
                                                cluster.cluster_index,
                                                cluster.cluster_balance,
                                                cluster.cluster_active
                                            ]
                                            ).call()
    cluster.balance = balance
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
    expand = 10000000
    block_per_day = 7200
    cluster_balance_now = int(cluster.balance_human * 1e18)
    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    operator_list = [l_models.Operator.objects.get(id=operator_id) for operator_id in operator_ids]
    operator_fee = sum(item.fee_human * 38264 for item in operator_list)

    liquidation_threshold_expand = (
                                           network_fee + operator_fee) * minimum_blocks_before_liquidation * cluster.validator_count * expand
    minimum_liquidation_collateral_expand = minimum_liquidation_collateral * expand
    if liquidation_threshold_expand < minimum_liquidation_collateral_expand:
        liquidation_threshold_expand = minimum_liquidation_collateral_expand
    valid_balance = cluster_balance_now - liquidation_threshold_expand

    burn_rate_per_day = (network_fee + operator_fee) * block_per_day * expand * cluster.validator_count
    est_days = valid_balance / burn_rate_per_day
    est_days = max(est_days, 0)
    return est_days


def process_cluster(formatted_log, update_keys={}):
    # args = formatted_log["args"]
    # operator_id_str = ",".join(args["operatorIds"])
    # owner = args["owner"].lower()
    #
    # cluster_info =
    print("formatted_log: ", formatted_log)
    args = formatted_log["args"]
    operator_id_list = [str(item) for item in args["operatorIds"]]
    operator_id_str = ",".join(operator_id_list)
    owner = args["owner"].lower()
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
    log_topic_0_hex = log["topics"][0].hex()
    if log_topic_0_hex == contract.events.ValidatorAdded.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ValidatorAdded.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log)

    elif log_topic_0_hex == contract.events.ValidatorRemoved.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ValidatorRemoved.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log)

    elif log_topic_0_hex == contract.events.ClusterLiquidated.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ClusterLiquidated.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log, update_keys={"liquidated": True})

    elif log_topic_0_hex == contract.events.ClusterReactivated.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ClusterReactivated.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log)

    elif log_topic_0_hex == contract.events.ClusterWithdrawn.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ClusterWithdrawn.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log)

    elif log_topic_0_hex == contract.events.ClusterDeposited.create_filter(fromBlock=0).builder.topics[0]:
        formatted_log = contract.events.ClusterDeposited.create_filter(fromBlock=0).format_entry(log)
        process_cluster(formatted_log)


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
