import pendulum
import requests
import datetime
from dataclasses import InitVar, dataclass
from airbyte_cdk.sources.declarative.types import Config
from typing import Any, Iterable, Mapping, Optional, Union, List, Tuple, MutableMapping
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from json.decoder import JSONDecodeError
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.types import StreamSlice, StreamState
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement

DEFAULT_END_DATE = pendulum.yesterday().date()
DEFAULT_CAMPAIGN_STATUS = "deleted,active,archived,dirty"
DEFAULT_DATE_FLAG = False


@dataclass
class ShortLivedTokenAuthenticator(DeclarativeAuthenticator):
    client_id: Union[InterpolatedString, str]
    secret_key: Union[InterpolatedString, str]
    url: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    token_key: Union[InterpolatedString, str] = "access_token"
    lifetime: Union[InterpolatedString, str] = ""

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._client_id = InterpolatedString.create(self.client_id, parameters=parameters)
        self._secret_key = InterpolatedString.create(self.secret_key, parameters=parameters)
        self._url = InterpolatedString.create(self.url, parameters=parameters)
        self._token_key = InterpolatedString.create(self.token_key, parameters=parameters)
        self._token = None
        self._session = requests.Session()

    def check_token(self):
        if self.config.get("credentials").get("type") == "access_token":
            self._token = self.config.get("credentials").get("access_token")
            if not self.validate_token(self._token):
                raise ConnectionError("Unauthorized token.")
        if self.config.get("credentials").get("type") == "OAuth":
            if not self._token or not self.validate_token(self._token):
                try:
                    response = requests.post(
                        url=self._url.default,
                        params={
                            "client_id": self.config.get("credentials").get("client_id"),
                            "client_secret": self.config.get("credentials").get("client_secret"),
                            "grant_type": "client_credentials"
                        }
                    )
                    response.raise_for_status()
                    self._token = response.json().get("access_token")
                except JSONDecodeError:
                    raise ConnectionError(response.text)

    def validate_token(self, access_token: str) -> bool:
        validate_url_auth = "https://oauth.audiencereport.com/oauth/validate_token"
        response = requests.post(
            url=validate_url_auth,
            params={
                "access_token": access_token
            }
        )
        if response.status_code == 200:
            authorization = response.json().get("authorized")
            if not authorization:
                return False
            return True
        else:
            return False

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        self.check_token()
        return f"Bearer {self._token}"

    @staticmethod
    def _get_time_interval(
            starting_date: Union[pendulum.datetime, str],
            ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if isinstance(starting_date, str):
            start_date = pendulum.parse(starting_date).date()
        if isinstance(ending_date, str):
            end_date = pendulum.parse(ending_date).date()
        else:
            end_date = DEFAULT_END_DATE
        if end_date < start_date:
            raise ValueError(
                f"""Provided start date has to be before end_date.
                                Start date: {start_date} -> end date: {end_date}"""
            )
        return start_date, end_date

    def get_request_params(
            self,
            *,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        params = {"type": "all", "sortDirection": "asc"}
        params.update({"status": DEFAULT_CAMPAIGN_STATUS})
        date_required = self.config.get("date_flag") if self.config.get("date_flag") else DEFAULT_DATE_FLAG
        if date_required:
            stream_start, stream_end = self._get_time_interval(self.config["start_date"], self.config["end_date"])
            params.update({"creationDate": stream_start, "reportEnd": stream_end})
        if next_page_token:
            params.update(**next_page_token)
        return params


class CampaignsStreamPagination(PageIncrement):
    max_records = 100
    start = 0

    def __post_init__(self, parameters: Mapping[str, Any]):
        self.param = parameters
        self.start_from_page = self.start

    def next_page_token(
            self,
            response: requests.Response,
            last_records: List[Mapping[str, Any]]
    ) -> Optional[Tuple[Optional[int], Optional[int]]]:
        self.start_from_page += self.max_records
        record_len = len(last_records)
        if record_len < self.max_records or record_len == 0:
            return None
        return self.page_size, self.start_from_page
