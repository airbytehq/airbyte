# Reading a page

In this section, we'll read a single page of records from the surveys endpoint.

## Write a failing test that reads a single page

We'll start by writing a failing integration test.

Create a file `unit_tests/integration/test_surveys.py`

```bash
mkdir unit_tests/integration
touch unit_tests/integration/test_surveys.py
code .
```

Copy this template to
`airbyte-integrations/connectors/source-survey-monkey-demo/unit_tests/integration/test_surveys.py`

```python
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Mapping, Optional
from unittest import TestCase

import freezegun
from airbyte_cdk.sources.source import TState
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse
from airbyte_protocol.models import ConfiguredAirbyteCatalog, SyncMode
from source_survey_monkey_demo import SourceSurveyMonkeyDemo

_A_CONFIG = {
    <TODO>
}
_NOW = <TODO>

@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    @HttpMocker()
    def test_read_a_single_page(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            HttpRequest(url=),
            HttpResponse(body=, status_code=)
        )

        output = self._read(_A_CONFIG, _configured_catalog(<TODO>, SyncMode.full_refresh))

        assert len(output.records) == 2

    def _read(self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, expecting_exception: bool = False) -> EntrypointOutput:
        return _read(config, configured_catalog=configured_catalog, expecting_exception=expecting_exception)

def _read(
    config: Mapping[str, Any],
    configured_catalog: ConfiguredAirbyteCatalog,
    state: Optional[Dict[str, Any]] = None,
    expecting_exception: bool = False
) -> EntrypointOutput:
    return read(_source(configured_catalog, config, state), config, configured_catalog, state, expecting_exception)


def _configured_catalog(stream_name: str, sync_mode: SyncMode) -> ConfiguredAirbyteCatalog:
    return CatalogBuilder().with_stream(stream_name, sync_mode).build()


def _source(catalog: ConfiguredAirbyteCatalog, config: Dict[str, Any], state: Optional[TState]) -> SourceSurveyMonkeyDemo:
    return SourceSurveyMonkeyDemo()
```

Most of this code is boilerplate. The most interesting section is the test

```python
    @HttpMocker()
    def test_read_a_single_page(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            HttpRequest(url=),
            HttpResponse(body=, status_code=)
        )

        output = self._read(_A_CONFIG, _configured_catalog(<TODO>, SyncMode.full_refresh))

        assert len(output.records) == 2
```

`http_mocker.get` is used to register mocked requests and responses. You can specify the URL, query
params, and request headers the connector is expected to send and mock the response that should be
returned by the server to implement fast integration test that can be used to verify the connector's
behavior without the need to reach the API. This allows the tests to be fast and reproducible.

Now, we'll implement a first test verifying the connector will send a request to the right endpoint,
with the right parameter, and verify that records are extracted from the data field of the response.

```python
_A_CONFIG = {
	"access_token": "access_token"
}
_NOW = datetime.now(timezone.utc)

@freezegun.freeze_time(_NOW.isoformat())
class FullRefreshTest(TestCase):

    @HttpMocker()
    def test_read_a_single_page(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?include=response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats"),
            HttpResponse(body="""
            {
  "data": [
    {
      "id": "1234",
      "title": "My Survey",
      "nickname": "",
      "href": "https://api.surveymonkey.com/v3/surveys/1234"
    },
    {
      "id": "1234",
      "title": "My Survey",
      "nickname": "",
      "href": "https://api.surveymonkey.com/v3/surveys/1234"
    }
  ],
  "per_page": 50,
  "page": 1,
  "total": 2,
  "links": {
    "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=50"
  }
}
""", status_code=200)
        )

        output = self._read(_A_CONFIG, _configured_catalog("surveys", SyncMode.full_refresh))

        assert len(output.records) == 2
```

Note that the test also required adding the "access_token" field to the config. We'll use this field
to store the API key obtained in the first section of the tutorial.

The test should fail because the expected request was not sent

```bash
poetry run pytest unit_tests/integration
```

> ValueError: Invalid number of matches for
> `HttpRequestMatcher(request_to_match=ParseResult(scheme='https', netloc='api.surveymonkey.com', path='/v3/surveys', params='', query='include=response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats', fragment='') with headers {} and body None), minimum_number_of_expected_match=1, actual_number_of_matches=0)`

We'll now remove the unit tests files. Writing unit tests is left as an exercise for the reader, but
it is highly recommended for any productionized connector.

```
rm unit_tests/test_incremental_streams.py unit_tests/test_source.py unit_tests/test_streams.py
```

Replace the content of
`airbyte-integrations/connectors/source-survey-monkey-demo/source_survey_monkey_demo/source.py` with
the following template:

```python
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator, TokenAuthenticator


class SurveyMonkeyBaseStream(HttpStream, ABC):
    def __init__(self, name: str, path: str, primary_key: Union[str, List[str]], data_field: str, **kwargs: Any) -> None:
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._data_field = data_field
        super().__init__(**kwargs)

    url_base = <TODO>

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"include": "response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if self._data_field:
            yield from response_json.get(self._data_field, [])
        else:
            yield from response_json

    @property
    def name(self) -> str:
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return self._path

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key


# Source
class SourceSurveyMonkeyDemo(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = <TODO>
        return [SurveyMonkeyBaseStream(name=<TODO>, path=<TODO>, primary_key=<TODO>, data_field=<TODO>, authenticator=auth)]
```

:::info This template restructures the code so its easier to extend. Specifically, it provides a
base class that can be extended with composition instead of inheritance, which is generally less
error prone.

:::

Then set the URL base

```python
url_base = "https://api.surveymonkey.com"
```

Set the query parameters:

```python
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"include": "response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats"}
```

and configure the authenticator, the name, the path, and the primary key

```python
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["access_token"])
        return [SurveyMonkeyBaseStream(name="surveys", path="v3/surveys", primary_key="id", data_field="data", authenticator=auth)]
```

We'll now update the
[connector specification](../../../understanding-airbyte/airbyte-protocol.md#actor-specification).
We'll add the access_token as a required property, making sure to flag it as an `airbyte_secret` to
ensure the value isn't accidentally leaked, and we'll specify its `order` should be 0 so it shows up
first in the Source setup page.

```yaml
documentationUrl: https://docsurl.com
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Survey Monkey Demo Spec
  type: object
  required:
    - access_token
  properties:
    access_token:
      type: string
      description: "Access token for Survey Monkey API"
      order: 0
      airbyte_secret: true
```

Let's now rename one of the mocked schema files to `surveys.json` so its used by our new stream, and
remove the second one as it isn't needed.

```
mv source_survey_monkey_demo/schemas/customers.json source_survey_monkey_demo/schemas/surveys.json
rm source_survey_monkey_demo/schemas/employees.json
```

The two tests should now pass

```
poetry run pytest unit_tests/
```

Now fill in the `secrets/config.json` file with your API access token

```json
{
  "access_token": "<TODO>"
}
```

and update the configured catalog so it knows about the newly created stream:

```json
{
  "streams": [
    {
      "stream": {
        "name": "surveys",
        "json_schema": {},
        "supported_sync_modes": ["full_refresh"]
      },
      "sync_mode": "full_refresh",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```

We can now run a read command to pull data from the endpoint:

```
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

The connector should've successfully read records.

```json
{
  "type": "LOG",
  "log": { "level": "INFO", "message": "Read 14 records from surveys stream" }
}
```

You can also pass in the `--debug` flag to see the real requests and responses sent and received.
It's also recommended to use these real requests as templates for the integration tests as they can
be more accurate the examples from API documentation.

In the [next section](./3-reading-multiple-pages.md), we'll implement pagination to read all surveys
from the endpoint# Reading a page
