#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
import pendulum
import json

from dateutil.relativedelta import relativedelta
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_alipay_worldfirst.auth import RSA256_Signature, get_authorization_header_str, date_time_fmt
from .streams import StatementList


# Source
class SourceAlipayWorldfirst(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:

        method = "POST"
        path = "/amsin/api/v1/business/account/inquiryStatementList"
        client_id = config["client_id"]
        private_key = config["private_key"]
        base_url = config["base_url"]

        current_ts = pendulum.now("utc")
        date_time = current_ts.strftime(date_time_fmt)
        end_time = date_time
        start_time = (current_ts + relativedelta(days=-1 * 30)).strftime(date_time_fmt)

        if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
            start_time = (current_ts + relativedelta(days=-1 * config["tunnel_method"]["days"])).strftime(date_time_fmt)
        else:
            start_time = config["tunnel_method"]["start_time"]
            end_time = config["tunnel_method"]["end_time"]

        body = {
            "startTime": start_time,
            "endTime": end_time,
            "pageSize": 10,
            "pageNumber": 1,
            "transactionTypeList": ["COLLECTION", "TRANSFER"],
        }
        body_str = str(json.dumps(body, separators=(",", ":")))
        res = get_authorization_header_str(method, path, client_id, private_key, date_time, body_str)

        header = {
            "Client-Id": client_id,
            "Signature": res,
            "Content-Type": "Content-Type: application/json; charset=UTF-8",
            "Request-Time": date_time,
        }
        resp = requests.post(url=base_url + path, headers=header, data=body_str)
        if resp.status_code == 200 and resp.json().get("result").get("resultStatus") == "S":
            return True, None
        return False, resp.json().get("result")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:

        client_id = config.get("client_id")
        base_url = config.get("base_url")
        private_key = config.get("private_key")

        start_time = None
        end_time = None
        period_in_days = None
        if config["tunnel_method"]["tunnel_method"] == "PERIODIC":
            period_in_days = config["tunnel_method"]["days"]
        else:
            start_time = config["tunnel_method"]["start_time"]
            end_time = config["tunnel_method"]["end_time"]
        key_str = {
            "url_base": base_url,
            "client_id": client_id,
            "private_key": private_key,
            "period_in_days": period_in_days,
            "start_time": start_time,
            "end_time": end_time,
            "source_name": config.get("source_name"),
            "rsa_signature": RSA256_Signature(client_id, private_key, base_url),
        }
        return [StatementList(**key_str)]
