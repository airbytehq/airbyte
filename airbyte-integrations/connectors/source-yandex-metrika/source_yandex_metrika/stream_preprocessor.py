#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import requests
import logging
from time import sleep
from typing import Any, List, Mapping, Tuple
from requests.adapters import HTTPAdapter, Retry
from urllib3.util.retry import RequestHistory

logger = logging.getLogger("airbyte")


class LoggedRetry(Retry):
    """
       Adding extra logs before making a retry request     
    """

    def __init__(self, *args, **kwargs):
        if kwargs.get('history'):
            latest_attempt: RequestHistory = kwargs["history"][-1]
            sleep_time = kwargs['backoff_factor'] * \
                (2 ** ((7 - kwargs['total']) - 1))
            logger.info(
                f'Retry on {latest_attempt.method} {latest_attempt.url}. Status code {latest_attempt.status}.'
                f' Exception: {latest_attempt.error}.'
                f' Sleep for {sleep_time} seconds and try again...'
            )
        super().__init__(*args, **kwargs)


class YandexMetrikaStreamPreprocessor:
    retries = LoggedRetry(
        total=7,
        backoff_factor=5,
        status_forcelist=[429, *range(500, 600)]
    )

    def __init__(self, stream_instance: "YandexMetrikaStream"):
        self.stream_instance = stream_instance
        self.session = requests.Session()
        for proto in ['http://', 'https://']:
            self.session.mount(proto, HTTPAdapter(max_retries=self.retries))

    def authorized_request_headers(self, stream_slice: Mapping[str, Any] = None):
        return dict(**self.stream_instance.request_headers(stream_slice=stream_slice),
                    **self.stream_instance._authenticator.get_auth_header())

    def request_params(self, stream_slice: Mapping[str, Any]):
        return self.stream_instance.request_params(stream_slice=stream_slice)

    @property
    def url_base(self):
        return self.stream_instance.url_base

    @property
    def counter_id(self):
        return self.stream_instance.counter_id

    def create_log_request(self, stream_slice: Mapping[str, Any]) -> int:
        url = self.url_base + f"counter/{self.counter_id}/logrequests"
        logger.info(f"Create log request for slice {stream_slice}: {url}")
        try:
            create_log_request_response = self.session.post(
                url,
                headers=self.authorized_request_headers(stream_slice),
                params=self.request_params(
                    stream_slice=stream_slice),
            )
            create_log_request_response_data = create_log_request_response.json()
        except:
            raise Exception(
                f'API error on create_log_request_response.json(). Response: {create_log_request_response.text}, Status code: {create_log_request_response.status_code}'
            )
        try:
            return create_log_request_response_data["log_request"]["request_id"]
        except:
            raise Exception(
                f'API error on create_log_request_response["log_request"]["request_id"]. Response: {create_log_request_response_data}'
            )

    def check_if_log_request_already_on_server(self, stream_slice: Mapping[str, Any], cached_available_log_requests: List[Mapping[str, Any]] = None) -> Tuple[bool, int]:
        # Return (True, <log_request_id>) if log request was found, otherwise return (False, None)
        available_log_requests = cached_available_log_requests or self.get_available_log_requests()
        params = self.request_params(stream_slice=stream_slice)
        fields_to_check = sorted(params["fields"].split(","))
        date_from_to_check, date_to_to_check = params["date1"], params["date2"]
        source_to_check = params["source"]

        for log_request in available_log_requests:
            if (
                fields_to_check == sorted(log_request["fields"])
                and date_from_to_check == log_request["date1"]
                and date_to_to_check == log_request["date2"]
                and source_to_check == log_request["source"]
            ):
                return True, log_request["request_id"]
        return False, None

    def wait_for_log_request_processed(self, log_request_id: str, stream_slice: str):
        processed_parts = []
        current_status = None
        invalid_api_requests_counter = 0
        while current_status != "processed":
            url = self.url_base + \
                f"counter/{self.counter_id}/logrequest/{log_request_id}"
            headers = self.authorized_request_headers()
            check_log_request_status_response = self.session.get(
                url,
                headers=headers,
                params=self.request_params(stream_slice=stream_slice),
            ).json()
            try:
                log_request = check_log_request_status_response["log_request"]
            except:
                if invalid_api_requests_counter == 3:
                    raise Exception(
                        'API request is invalid on check_log_request_status_response["log_request"] '
                        f"on 3th retry. Response: {check_log_request_status_response}"
                    )
                invalid_api_requests_counter += 1

                logger.info(
                    "Warning: API request is invalid on check_log_request_status_response"
                    f'["log_request"]. Response: {check_log_request_status_response}'
                )
                logger.info("Sleep for 30 seconds and try again...")
                sleep(30)
                continue
            if log_request.get("parts"):
                processed_parts = log_request.get("parts")
            current_status = log_request["status"]
            logger.info(
                f"Log request {url} current status: {current_status}")
            if current_status == "processed":
                break
            sleep(30)
        logger.info(f"Processed parts for slice { processed_parts}")
        return {**stream_slice, 'processed_parts': processed_parts, 'log_request_id': log_request_id}

    def get_available_log_requests(self):
        url = self.url_base + f"counter/{self.counter_id}/logrequests"
        headers = self.authorized_request_headers()
        response_data = self.session.get(
            url, headers=headers)
        try:
            return response_data.json()["requests"]
        except:
            raise Exception(
                f"API Error on clean_all_log_requests (URL: {url} Headers: {headers}): {response_data.text}")

    def clean_all_log_requests(self):
        logger.info(f"Clean All Log Requests")

        available_log_requests = self.get_available_log_requests()
        for log_request in available_log_requests:
            if log_request["status"] not in ["cleaned_by_user", "cleaned_automatically_as_too_old", "canceled", "processing_failed"]:
                cleaned_log_request = self.clean_log_request(
                    log_request["request_id"])
                logger.info(f"Cleaned log request: {cleaned_log_request}")

    def check_log_request_ability(self, stream_slice: str) -> Tuple[bool, any]:
        url = self.url_base + f"counter/{self.counter_id}/logrequests/evaluate"
        headers = self.authorized_request_headers(stream_slice=stream_slice)
        params = self.request_params(stream_slice=stream_slice)

        for i in range(5):
            try:
                resp = self.session.get(url, headers=headers, params=params)
                resp_data = resp.json()
                eval = resp_data.get("log_request_evaluation", {})
                if not eval.get("possible"):
                    return (
                        False,
                        f"Log request for {stream_slice} slice is not possible to create. Max possible days quantity - "
                        + str(eval.get("max_possible_day_quantity")) +
                        f'(Response text: {resp.text})'
                    )

                return True, None
            except Exception as e:
                logger.info(
                    f"Failed to get check_log_request_ability response: url - {url}, headers - {headers}, params' \
                    f' - {params}. Sleep for 10 seconds... (retry={i}). Exception: {e}"
                )
                sleep(10)

    def check_stream_slices_ability(self) -> Tuple[bool, any]:
        available_log_requests = self.get_available_log_requests()
        for raw_stream_slice in self.stream_instance.stream_slices():
            is_already_on_server, on_server_log_request_id = self.check_if_log_request_already_on_server(
                stream_slice=raw_stream_slice, cached_available_log_requests=available_log_requests)
            if is_already_on_server:
                logger.info(
                    f"Check raw slice {raw_stream_slice}. Status: Already on server. Log request ID: {on_server_log_request_id}")
                continue
            is_possible, is_possible_message = self.check_log_request_ability(
                raw_stream_slice)
            logger.info(
                f"Check raw slice {raw_stream_slice}. Is possible: {is_possible}")
            if not is_possible:
                return False, is_possible_message
        return True, None

    def clean_log_request(self, log_request_id):
        url = self.url_base + \
            f"counter/{self.counter_id}/logrequest/{log_request_id}/clean"
        logger.info(f"Clean log request {url}...")
        return self.session.post(url, headers=self.authorized_request_headers()).json()
