import requests
import pandas

if __name__ == '__main__':
    response = requests.get("https://api.ssv.network/api/v3/prater/validators/?page=1&perPage=1000")
    data = response.json()
    exporter_operator_list = [{"public_key": "0x" + item["public_key"], "status": item["status"]} for item in data["validators"]]

    response = requests.get("https://alert.hellman.team/api/v1/ssv/validators?page_size=1000")
    data = response.json()
    alert_operator_list = [
        {"public_key": item["public_key"], "active": "Active" if item["active"] else "Inactive"} for item in data["results"]]

    exporter_operator_list_df = pandas.DataFrame(exporter_operator_list)
    alert_operator_list_df = pandas.DataFrame(alert_operator_list)

    joined_df = pandas.merge(exporter_operator_list_df, alert_operator_list_df, how="outer", on=["public_key"])

    # joined_df = exporter_operator_list_df.join(alert_operator_list_df, on="id")

    joined_df.to_csv("validator_status.csv", index=False)


