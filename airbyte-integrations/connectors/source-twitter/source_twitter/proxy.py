import logging
import time

from requests.exceptions import Timeout
from requests_oauthlib import OAuth1Session
from twitter_ads.http import Request as TwitterRequest, Response

logger = logging.getLogger(__name__)


class Request:
    def patched_oauth_request(self):
        headers = {"user-agent": self.__user_agent()}
        if "headers" in self.options:
            headers.update(self.options["headers"].copy())

        # DEPRECATED: internal-only (Should pass a header to the client)
        if "x-as-user" in self._client.options:
            headers["x-as-user"] = self._client.options.get("x-as-user")
        # Add headers from the client to the request (Client headers take priority)
        for key, val in self._client.headers.items():
            headers[key] = val
        params = self.options.get("params", None)
        data = self.options.get("body", None)
        files = self.options.get("files", None)
        stream = self.options.get("stream", False)

        handle_rate_limit = self._client.options.get("handle_rate_limit", False)
        retry_max = self._client.options.get("retry_max", 0)
        retry_delay = self._client.options.get("retry_delay", 1500)
        retry_on_status = self._client.options.get("retry_on_status", [500, 503])
        retry_on_timeouts = self._client.options.get("retry_on_timeouts", False)
        timeout = self._client.options.get("timeout", None)
        retry_count = 0
        retry_after = None
        timeout = self._client.options.get("timeout", None)

        consumer = OAuth1Session(
            self._client.consumer_key,
            client_secret=self._client.consumer_secret,
            resource_owner_key=self._client.access_token,
            resource_owner_secret=self._client.access_token_secret,
        )

        proxy_protocol = self.proxy_protocol
        proxy_host = self.proxy_host
        proxy_port = self.proxy_port
        proxy_login = self.proxy_login
        proxy_password = self.proxy_password
        proxy_url = f"{proxy_protocol}://{proxy_login}:{proxy_password}@{proxy_host}:{proxy_port}"
        consumer.proxies = {"all": proxy_url}

        url = self.__domain() + self._resource
        method = getattr(consumer, self._method)

        while retry_count <= retry_max:
            try:
                response = method(url, headers=headers, data=data, params=params, files=files, stream=stream, timeout=timeout)
            except Timeout as e:
                if retry_on_timeouts:
                    if retry_count == retry_max:
                        raise Exception(e)
                    logger.warning("Timeout occurred: resume in %s seconds" % (int(retry_delay) / 1000))
                    time.sleep(int(retry_delay) / 1000)
                    retry_count += 1
                    continue
                raise Exception(e)

            # do not retry on 2XX status code
            if 200 <= response.status_code < 300:
                break

            if handle_rate_limit and retry_after is None:
                rate_limit_reset = response.headers.get("x-account-rate-limit-reset") or response.headers.get("x-rate-limit-reset")

                if response.status_code == 429:
                    retry_after = int(rate_limit_reset) - int(time.time())
                    logger.warning("Request reached Rate Limit: resume in %d seconds" % retry_after)
                    time.sleep(retry_after + 5)
                    continue

            if retry_max > 0:
                if response.status_code not in retry_on_status:
                    break
                time.sleep(int(retry_delay) / 1000)

            retry_count += 1

        raw_response_body = response.raw.read() if stream else response.text

        return Response(response.status_code, response.headers, body=response.raw, raw_body=raw_response_body)


def set_twitter_proxy(protocol: str, host: str, port: str, login: str, password: str) -> None:
    TwitterRequest.proxy_protocol = protocol
    TwitterRequest.proxy_host = host
    TwitterRequest.proxy_port = port
    TwitterRequest.proxy_login = login
    TwitterRequest.proxy_password = password
    TwitterRequest._Request__oauth_request = Request.patched_oauth_request
