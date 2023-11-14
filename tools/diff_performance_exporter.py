import requests
import pandas

if __name__ == '__main__':
    response = requests.get("https://api.ssv.network/api/v4/mainnet/operators/?page=1&perPage=1000")
    data = response.json()
    exporter_operator_list = [{"id": item["id"], "name": item["name"], "exporter_performance": item["performance"]["24h"], "validators_count": item["validators_count"]} for item in data["operators"]]

    response = requests.get("https://alert.hellman.team/api/v1/ssv/operators?page_size=1000")
    data = response.json()
    alert_operator_list = [
        {"id": item["id"], "alert_performance": item["performance_1day"],
         "alert_validators_count": item["validator_count"]} for item in data["results"]]

    exporter_operator_list_df = pandas.DataFrame(exporter_operator_list)
    alert_operator_list_df = pandas.DataFrame(alert_operator_list)

    joined_df = pandas.merge(exporter_operator_list_df, alert_operator_list_df, how="outer", on=["id"])

    # joined_df = exporter_operator_list_df.join(alert_operator_list_df, on="id")

    joined_df.to_csv("performance.csv", index=False)


