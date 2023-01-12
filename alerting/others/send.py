import json
import logging
import os
from urllib.parse import quote

import jinja2

import requests
from django.conf import settings

from alibabacloud_dm20151123.client import Client as Dm20151123Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dm20151123 import models as dm_20151123_models
from alibabacloud_tea_util import models as util_models
from django.core.signing import Signer

logger = logging.getLogger(__name__)


def send(to_type, to, id, name, description, user_name):
    signer = Signer()
    sign = signer.sign(str(id))
    name_encoded = quote(name)
    ack_link = f"{settings.BASE_URL}/confirm/{id}/{sign}?name={name_encoded}"
    update_link = f"{settings.BASE_URL}/subscribe"
    if to_type == "email":
        send_to_email(to, id, name, ack_link, update_link,  description, user_name)
    elif to_type == "discord":
        send_to_discord(to, id, name, ack_link, update_link, description, user_name)
    elif to_type == "webhook":
        send_to_webhook(to, id, name, ack_link, update_link, description, user_name)
    else:
        raise Exception(f"unknown to_type: {to_type}")


# send failed raise exception
def send_to_email(to, id, name, ack_link, update_link, description, user_name):
    # print(os.getcwd())
    # html_template = "id: <h2>{{ id }}<h2><br/>name: <h2>{{ name }}<h2><br/>acknowledgeLink: <h2>{{ ack_link }}<h2><br/>"
    with open("alerting/others/email.html") as f:
        html_template = f.read()
    template = jinja2.Template(html_template)
    html_message = template.render(id=id, name=name, ack_link=ack_link, update_link=update_link,
                                   description=description, user_name=user_name)
    # message = strip_tags(html_message)
    # send_mail(
    #     subject="Hellman Alert",
    #     message=message,
    #     from_email=settings.EMAIL_HOST_USER,
    #     recipient_list=[to],
    #     # html_message=html_message
    # )

    config = open_api_models.Config(
        # 必填，您的 AccessKey ID,
        access_key_id=settings.ALIYUN_ACCESS_KEY,
        # 必填，您的 AccessKey Secret,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
    )
    # 访问的域名
    config.endpoint = f'dm.aliyuncs.com'
    client = Dm20151123Client(config)
    single_send_mail_request = dm_20151123_models.SingleSendMailRequest(
        account_name=settings.ALIYUN_EMAIL_ACCOUNT_NAME,
        address_type=1,
        reply_to_address="false",
        subject="Hellman Alert",
        to_address=to,
        html_body=html_message,
    )
    runtime = util_models.RuntimeOptions()
    response = client.single_send_mail_with_options(single_send_mail_request, runtime)

    #
    # try:
    #     # 复制代码运行请自行打印 API 的返回值
    # except Exception as error:
    #     # 如有需要，请打印 error
    #     UtilClient.assert_as_string(error.message)


# send failed raise exception
def send_to_discord(to, id, name, ack_link, update_link, description, user_name):
    # content = f"Hellman Alert\nID: {id}\nName: {name}\nAcknowledge Link: {ack_link}"
    content = f"""Dear Client {user_name},
Thanks for subscribing the Hellman Alerts!
Alert ID: {id}
Alert Nickname: {name}
{description}

Please 'Acknowledge' if you do not need a reminder and 'Update' if you wish to modify the criteria.
Acknowledge Link: {ack_link}
Update Link {update_link}
Best regards
Hellman Team"""
    request_body = {
        "content": content
    }
    headers = {
        "Content-Type": "application/json"
    }
    proxies = None
    if settings.DISCORD_HTTPS_PROXY:
        proxies = {
            "https": settings.DISCORD_HTTPS_PROXY
        }
    response = requests.post(url=to,
                             headers=headers,
                             data=json.dumps(request_body),
                             timeout=60,
                             proxies=proxies)
    if response.status_code > 300:
        raise Exception("send to discord error code: {} body:", response.status_code, response.text)


def send_to_webhook(to, id, name, ack_link, update_link, description, user_name):
    request_body = {
        "title": "Hellman Alert",
        "user_name": user_name,
        "id": id,
        "subscribe_name": name,
        "description": description,
        "acknowledge_link": ack_link,
        "update_link": update_link
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url=to,
                             headers=headers,
                             data=json.dumps(request_body),
                             timeout=60)
    if response.status_code > 300:
        raise Exception("send to webhook error code: {} body:", response.status_code, response.text)