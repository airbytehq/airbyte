"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import math
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from base_python import AbstractSource, HttpStream, Stream
from base_python.cdk.streams.auth.token import TokenAuthenticator


class DbtCloudStream(HttpStream, ABC):
    url_base = 'https://cloud.getdbt.com/api/v2/'

    def __init__(self, account_id: str, **kwargs):
        super().__init__(**kwargs)
        self.account_id = account_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(self,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, any] = None,
                       next_page_token: Mapping[str, Any] = None
                       ) -> MutableMapping[str, Any]:
        # DBT uses offset and limit to paginate.
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get("data", [])


class IncrementalDbtCloudStream(DbtCloudStream, ABC):
    state_checkpoint_interval = math.inf

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    def get_updated_state(self,
                          current_stream_state: MutableMapping[str, Any],
                          latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        return {self.cursor_field: max(latest_record.get(self.cursor_field),
                                       current_stream_state.get(self.cursor_field, 0))}

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["start_date"] = stream_state.get(self.cursor_field)
        return params


class Accounts(DbtCloudStream):
    name = "accounts"
    primary_key = "id"

    def path(self, **kwargs):
        return 'accounts'


class Projects(DbtCloudStream):
    name = "projects"
    primary_key = ""

    def path(self, **kwargs):
        return f"/accounts/{self.account_id}/projects"


class Jobs(DbtCloudStream):
    name = "jobs"
    primary_key = ""

    def path(self, **kwargs) -> str:
        return f"/accounts/{self.account_id}/jobs"


class Runs(IncrementalDbtCloudStream):
    name = "runs"
    primary_key = ""
    cursor_field = "created_at"

    def path(self, **kwargs):
        return f"/accounts/{self.account_id}/runs"


class RunArtifacts(DbtCloudStream):
    name = "run_artifacts"
    primary_key = ""

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        return f"accounts/{self.account_id}/runs/{stream_slice['id']}/artifacts/"

    def request_params(self, stream_slice: Mapping[str, Any] = None, **kwargs):
        params = super().request_params(stream_slice=stream_slice, **kwargs)
        params["runs"] = stream_slice["id"]
        return params

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        runs_streams = Runs(authenticator=self.authenticator, account_id=self.account_id)
        for runs in runs_streams.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"id": runs["id"]}, **kwargs)


class SourceDbtCloud(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        token = config['authorization']
        account_id = config['account_id']

        get_accounts = "https://cloud.getdbt.com/api/v2/accounts/{accountId}".format(accountId=account_id)

        try:
            requests.get(
                url=get_accounts,
                headers={'Authorization': "Bearer " + token},
            )
            return True, None
        except requests.HTTPError as error:
            return False, error

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config['authorization'])

        args = {
            "authenticator": auth,
            "account_id": config["account_id"]
        }

        return [
            Accounts(**args),
            Projects(**args),
            Jobs(**args),
            Runs(**args),
            RunArtifacts(**args)
        ]
