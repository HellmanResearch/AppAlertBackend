import logging
import subprocess

from web3 import Web3
from eth_abi.packed import encode_packed
from .. import models as l_models
from django.db import IntegrityError
from django.conf import settings

logger = logging.getLogger("tasks")


def save_cluster(event):
    args = event["args"]
    # cluster_id = encode_packed(["address", "uint64[]"], [args["owner"], args["operatorIds"]]).hex()
    cluster_id = Web3.solidity_keccak(["address", "uint64[]"], [args["owner"], args["operatorIds"]]).hex()
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
    except Exception as exc:
        logger.warning(f"save cluster error: {exc}")


def get_cluster_est_days(cluster: l_models.Cluster,
                         network_fee,
                         network_fee_index,
                         cluster_network_fee_index,
                         cluster_validator_count,
                         cluster_index,
                         minimum_blocks_before_liquidation,
                         minimum_liquidation_collateral):
    # owner = "0x7778996a5a744709e1e3dca090143c0c16ab3031"
    # operator_ids = [70, 76, 100, 101]
    # cluster = [2, 3695307536, 3135734800, 5075286612870000000, True]
    # block_number = w3.eth.block_number
    # cluster_index_now = 0
    # burn_rate = 0
    expand = 10000000

    cluster_balance_now = int(cluster.balance_human * 1e18)

    # cluster_balance_now = 5856473781450000000

    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    operator_list = [l_models.Operator.objects.get(id=operator_id) for operator_id in operator_ids]

    operator_fee_sum = sum([operator.fee_human * 38264 for operator in operator_list])
    operator_fee_sum_expand = operator_fee_sum * expand
    operator_snapshot_index_sum = sum([operator.snapshot_index * 1e18 for operator in operator_list])

    # operator_snapshot_index_sum = 0
    # operator_fee_sum = 0
    # for operator_id in operator_ids:
    #     operator = contract.functions.operators(operator_id).call()
    #     fee = operator[1]
    #     snapshot = operator[3]
    #     # cluster_index_now += snapshot[1] + (block_number - snapshot[0]) * fee
    #     # burn_rate += fee
    #     operator_fee_sum += fee
    #     operator_snapshot_index_sum += snapshot[1]

    # network_fee, network_fee_index, network_fee_index_block_number = contract.functions.network().call()
    # print("network_fee, network_fee_index, network_fee_index_block_number: ", network_fee, network_fee_index,
    #       network_fee_index_block_number)

    # usage_network_fee_snapshot =

    # current_network_fee_index = network_fee_index + (block_number - network_fee_index_block_number) * network_fee

    # cluster_validator_count = cluster.validator_count
    # # cluster_network_fee_index = cluster[1]
    # cluster_index = cluster[2]
    # cluster_balance = cluster[3]

    # usage_network_fee = (current_network_fee_index - cluster_network_fee_index) * cluster_validator_count

    # usage = (cluster_index_now - cluster_index) * cluster_validator_count + usage_network_fee
    # usage_expand = usage * 10000000
    # cluster_balance_now = 0 if usage_expand > cluster_balance else (cluster_balance - usage_expand)

    # network_fee, network_fee_index, network_fee_index_block_number = contract.functions.network().call()
    # minimum_blocks_before_liquidation = contract.functions.minimumBlocksBeforeLiquidation().call()
    # minimum_liquidation_collateral = contract.functions.minimumLiquidationCollateral().call()
    minimum_liquidation_collateral_expand = minimum_liquidation_collateral * expand

    network_fee_expand = network_fee * expand
    liquidation_threshold_expand = minimum_blocks_before_liquidation * (
            operator_fee_sum + network_fee) * cluster_validator_count
    # liquidation_threshold_expand = liquidation_threshold * expand

    liquidation_threshold_amount = max(liquidation_threshold_expand, minimum_liquidation_collateral_expand)

    print("liquidation_threshold_expand: ", liquidation_threshold_expand)

    usage_network_fee_snapshot = network_fee_index - cluster_network_fee_index
    usage_operator_fee_snapshot = operator_snapshot_index_sum - cluster_index

    usage_network_fee_snapshot_expand = usage_network_fee_snapshot * expand
    usage_operator_fee_snapshot_expand = usage_operator_fee_snapshot * expand

    # valid_balance = cluster_balance_now - liquidation_threshold_amount - usage_network_fee_snapshot_expand - usage_operator_fee_snapshot_expand

    # usage_expand = cluster_balance
    #
    # usage = usage_expand / 1e7
    # usage_network_fee = (cluster_index_now - cluster_index) * cluster_validator_count - usage
    # current_network_fee_index = (usage_network_fee / cluster_validator_count) + cluster_network_fee_index

    # usage = (sum([snapshot[1] + (block_number - snapshot[0]) * fee for item in operator_ids]) - cluster_index) * cluster_validator_count + ((current_network_fee_index - cluster_network_fee_index) * cluster_validator_count)
    block_per_day = 7200
    network_burn_per_day = network_fee * block_per_day * cluster_validator_count
    operator_burn_per_day = operator_fee_sum * block_per_day * cluster_validator_count
    # cluster_balance_now = 5856473781450000000

    available_balance = cluster_balance_now - liquidation_threshold_amount

    # x * (network_burn_per_day + operator_burn_per_day) = available_balance

    est_days = available_balance / ((network_burn_per_day + operator_burn_per_day) * expand)
    est_days = max(0, est_days)
    return est_days


# def get_cluster_is_liquidated(cluster):
#     balance = contract.functions.getBalance(cluster.owner,
#                                             operator_ids,
#                                             [
#                                                 cluster_validator_count,
#                                                 cluster_network_fee_index,
#                                                 cluster_index,
#                                                 cluster_balance,
#                                                 cluster_active
#                                             ]
#                                             ).call()


def update_cluster(cluster,
                   contract,
                   network_fee,
                   network_fee_index,
                   minimum_blocks_before_liquidation,
                   minimum_liquidation_collateral):
    cmd = f"cd {settings.SSV_CLUSTER_SCANNER};yarn cli -n {settings.ETH_URL} -ca {settings.SSV_ADDRESS} -oa {cluster.owner} -oids {cluster.operator_ids}"
    logger.info(f"cmd: {cmd}")
    timeout = 20
    try:
        cp = subprocess.run(cmd, shell=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"timeout ({timeout}s)")
    if cp.returncode != 0:
        raise Exception(f"run cmd failed cp.returncode: {cp.returncode} cp.stdout: {cp.stdout} cp.stderr: {cp.stderr}")
    try:
        cluster_validator_count = int(cp.stdout.split('"validatorCount": "')[1].split('"')[0])
        cluster_network_fee_index = int(cp.stdout.split('"networkFeeIndex": "')[1].split('"')[0])
        cluster_index = int(cp.stdout.split('"index": "')[1].split('"')[0])
        cluster_balance = int(cp.stdout.split('"balance": "')[1].split('"')[0])
        cluster_active = cp.stdout.split('"active": ')[1].split('\n')[0]
        cluster_active = True if cluster_active == "true" else False
    except Exception as exc:
        raise Exception(f"parse stdout error: {exc}")
    operator_ids = [int(item) for item in cluster.operator_ids.split(",")]
    balance = contract.functions.getBalance(cluster.owner,
                                            operator_ids,
                                            [
                                                cluster_validator_count,
                                                cluster_network_fee_index,
                                                cluster_index,
                                                cluster_balance,
                                                cluster_active
                                            ]
                                            ).call()
    cluster.active = cluster_active
    cluster.balance_human = balance / 1e18
    cluster.validator_count = cluster_validator_count
    cluster.save()

    try:
        est_days = get_cluster_est_days(cluster=cluster,
                                        network_fee=network_fee,
                                        network_fee_index=network_fee_index,
                                        cluster_network_fee_index=cluster_network_fee_index,
                                        cluster_validator_count=cluster_validator_count,
                                        cluster_index=cluster_index,
                                        minimum_blocks_before_liquidation=minimum_blocks_before_liquidation,
                                        minimum_liquidation_collateral=minimum_liquidation_collateral)
        cluster.est_days = est_days
        cluster.save()
    except Exception as exc:
        logger.warning(f"get_cluster_est_days cluster_id: {cluster.id} error: {exc}")


    try:
        liquidated = contract.functions.isLiquidated(cluster.owner,
                                                     operator_ids,
                                                     [
                                                         cluster_validator_count,
                                                         cluster_network_fee_index,
                                                         cluster_index,
                                                         cluster_balance,
                                                         cluster_active
                                                     ]
                                                     ).call()
        cluster.liquidated = liquidated
        cluster.save()
    except Exception as exc:
        logger.warning(f"update liquidated error: cluster_id: {cluster.id} exc: {exc}")
