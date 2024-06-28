import logging
from datetime import datetime, timedelta
from typing import Iterable, Mapping, Optional, Any, List, Union, MutableMapping

import requests
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_protocol.models import SyncMode


class ApplovinStream(HttpStream):
    url_base = "https://o.applovin.com/campaign_management/v1/"
    use_cache = True  # it is used in all streams

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 500:
            print("Received error: " + str(response.status_code) + " " + response.text)
            # logging.warning("URL: " + str(response.url))
            # logging.warning("Status Code: " + str(response.status_code))
            # logging.warning("Reason: " + str(response.reason))
            # logging.warning("HTTP Version: " + str(response.raw.version))
            #
            # logging.warning("\n---- HEADERS ----")
            # for key, value in response.headers.items():
            #     logging.warning(f"{str(key)}: {str(value)}")
            #
            # logging.warning("\n---- COOKIES ----")
            # for name, value in response.cookies.items():
            #     logging.warning(f"{str(name)}: {str(value)}")
            #
            # logging.warning("\n---- CONTENT ----")
            # logging.warning(response.text)
            #
            # logging.warning("\n---- REDIRECT HISTORY ----")
            # for resp in response.history:
            #     logging.warning(f"Redirected to {resp.url} with status code {resp.status_code}")
            #
            # logging.warning("\n---- REQUEST INFO ----")
            # logging.warning("Request Method:" + str(response.request.method))
            # logging.warning("Request URL:" + str(response.request.url))
            # logging.warning("Request Headers:")
            #
            # for key, value in response.request.headers.items():
            #     logging.warning(f"{str(key)}: {str(value)}")
            #
            # if response.request.body:
            #     logging.warning("\nRequest Body:" + str(response.request.body))
            #
            # logging.warning("\n---- OTHER INFO ----")
            # logging.warning("Elapsed Time:" + str(response.elapsed))
            # logging.warning("Encoding:" + str(response.encoding))
            # logging.warning("Content Length:" + str(len(response.content)))

            return True
        if response.status_code == 429 or 501 <= response.status_code < 600:
            return True
        else:
            return False

    def generate_dummy_record(self):
        """
        During schema checks (when `read_records` is called just to compare schemas) we may return the
        already existing schema that is hardcoded into json file, this avoids a useless API call
        :return:
        """
        schema = self.get_json_schema()
        dummy_record = {}
        for field, details in schema['properties'].items():
            if 'string' in details['type']:
                dummy_record[field] = 'dummy_string'
            elif 'integer' in details['type'] or 'number' in details['type']:
                dummy_record[field] = 123
            elif 'boolean' in details['type']:
                dummy_record[field] = True
        return dummy_record


class Campaigns(ApplovinStream):
    primary_key = "campaign_id"
    use_cache = True

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        super().__init__(
            authenticator=authenticator,
        )

    def path(self, **kwargs) -> str:
        return "campaigns"


class CampaignsSubStream(HttpSubStream, ApplovinStream):
    backoff = 120
    raise_on_http_errors = False
    use_cache = False

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        super().__init__(
            authenticator=authenticator,
            parent=Campaigns(authenticator=authenticator, config=config),
        )

    # as of now Applovin's rate limit is around 2000 request per *hour*
    @property
    def max_retries(self) -> Union[int, None]:
        return 10

    @property
    def retry_factor(self) -> float:
        return 120.0

    @property
    def max_time(self) -> float:
        return 14400

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        campaigns = Campaigns(authenticator=self._session.auth, config=self.config)
        campaigns_records = list(campaigns.read_records(sync_mode=SyncMode.full_refresh))
        tracking_method_filter = self.config.get("filter_campaigns_tracking_methods")
        for campaign in campaigns_records:
            if (not tracking_method_filter or
                    (tracking_method_filter and campaign["tracking_method"] in tracking_method_filter)):
                yield {"campaign_id": campaign["campaign_id"]}
                continue


class Creatives(CampaignsSubStream):
    primary_key = "id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"creative_sets/{campaign_id}"


class Targets(CampaignsSubStream):
    primary_key = "campaign_id"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        campaign_id = stream_slice["campaign_id"]
        return f"campaign_targets/{campaign_id}"

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any] = None, **kwargs) -> Iterable[Mapping]:
        record = response.json()
        record["campaign_id"] = stream_slice["campaign_id"]
        yield record


class ApplovinIncrementalMetricsStream(ApplovinStream, IncrementalMixin):
    url_base = "https://r.applovin.com/"
    report_type = ""
    cursor_field = "day"
    page_size = 200000

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        self._state = {}
        self.offset = 0
        self.counter = 0
        super().__init__(
            authenticator=authenticator,
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value[self.cursor_field]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_count = response.json()["count"]
        print(f"Page count: {str(response_count)}")
        if response_count < self.page_size:
            return None
        else:
            self.offset += response_count
            return {
                "offset": self.offset
            }

    def read_records(
            self,
            sync_mode: SyncMode,
            cursor_field: Optional[List[str]] = None,
            stream_slice: Optional[Mapping[str, Any]] = None,
            stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        default_start_date = self.config["start_date"]
        if stream_state is None:
            print("generated a dummy record")
            return self.generate_dummy_record()

        self.offset = 0  # very important, reset offset for every slice
        print(f"Slice {str(stream_slice)}, state {str(stream_state)}")

        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            record_date = record[self.cursor_field]
            state_date = self.state.get(self.cursor_field)
            self.state = {self.cursor_field: max(record_date, state_date or default_start_date)}
            record_with_numeric_types = self._cast_types(record)
            yield record_with_numeric_types

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        print(
            f"Request_params of {self.report_type}: {str(stream_state)}, {str(stream_slice)}, date {str(stream_slice['date'])}, offset {self.offset}, limit {self.page_size}")
        return {
            "api_key": self.config["reporting_api_key"],
            "start": stream_slice["date"],
            "end": stream_slice["date"],
            "format": "json",
            "report_type": self.report_type,
            "columns": self.columns,
            "offset": self.offset,
            "limit": self.page_size
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        response_json = response.json()
        yield from response_json["results"]

    def _cast_types(self, record):
        for key, value in record.items():
            # Attempt to cast to integer
            if value.isdigit():
                record[key] = int(value)
            else:
                try:
                    record[key] = float(value)
                except ValueError:
                    # Keep the value as string if it cannot be casted to numeric
                    pass
        return record


    @property
    def columns(self):
        schema = self.get_json_schema()
        return ",".join(schema['properties'].keys())

    def stream_slices(
            self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = datetime.now()
        end_date = datetime.now()
        if stream_state and stream_state.get(self.cursor_field):
            start_date = datetime.strptime(self.state[self.cursor_field], '%Y-%m-%d')

        start_date = start_date - timedelta(days=7)

        num_days = (end_date - start_date).days
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(num_days + 1)]

        print(f"Slices: {str(dates)}")
        for date in dates:
            yield {"date": date}
            continue


class PublisherReports(ApplovinIncrementalMetricsStream):
    report_type = "publisher"
    primary_key = ["zone_id", "ad_type", "platform", "day", "hour", "placement", "size", "package_name", "bidding_integration"]

    def path(self, **kwargs) -> str:
        return "report"


class AdvertiserReports(ApplovinIncrementalMetricsStream):
    report_type = "advertiser"
    primary_key = ["ad_id", "ad_type", "platform", "day", "external_placement_id"]

    def path(self, **kwargs) -> str:
        return "report"


class ProbabilisticPublisherReports(ApplovinIncrementalMetricsStream):
    report_type = "publisher"
    primary_key = ["country", "ad_type", "platform", "day", "hour", "size"]

    def path(self, **kwargs) -> str:
        return "probabilisticReport"


class ProbabilisticAdvertiserReports(ApplovinIncrementalMetricsStream):
    report_type = "advertiser"
    primary_key = ["ad_id", "ad_type", "platform", "day", "external_placement_id"]

    def path(self, **kwargs) -> str:
        return "probabilisticReport"
