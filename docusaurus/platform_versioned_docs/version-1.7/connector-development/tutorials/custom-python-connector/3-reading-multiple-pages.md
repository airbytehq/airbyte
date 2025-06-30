# Read multiple pages

In this section, we'll implement pagination to read all the records available in the surveys
endpoint.

Again, we'll start by writing a failing test for fetching multiple pages of records

```python
    @HttpMocker()
    def test_read_multiple_pages(self, http_mocker: HttpMocker) -> None:

        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?include=response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats&per_page=1000"),
            HttpResponse(body="""
            {
  "data": [
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
    "self": "https://api.surveymonkey.com/v3/surveys?page=1&per_page=50",
    "next": "https://api.surveymonkey.com/v3/surveys?include=response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats&per_page=1000&page=2"
  }
}
""", status_code=200)
        )
        http_mocker.get(
            HttpRequest(url="https://api.surveymonkey.com/v3/surveys?include=response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats&per_page=1000&page=2"),
            HttpResponse(body="""
            {
  "data": [
    {
      "id": "5678",
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

These tests now have a lot of duplications because we keep pasting the same response templates. You
can look at the
[source-stripe connector for an example of how this can be DRY'd](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/unit_tests/integration/test_cards.py).

The test should fail because the request wasn't matched:

```bash
poetry run pytest unit_tests
```

> ValueError: Invalid number of matches for
> `HttpRequestMatcher(request_to_match=ParseResult(scheme='https', netloc='api.surveymonkey.com',
> path='/v3/surveys', params='', query='page=2&per_page=100', fragment='')

First, we'll update the request parameters to only be set if this is not a request. If submitting a
paginated request, we'll use the parameters coming from the response.

```python
# add next library to import section
from urllib.parse import urlparse
```

```python
# Create a pagination constant
_PAGE_SIZE: int = 1000
```

```python
    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            return urlparse(next_page_token["next_url"]).query
        else:
            return {"include": "response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats",
                    "per_page": _PAGE_SIZE}
```

Then we'll extract the next_page_token from the response

```python
   def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        links = response.json().get("links", {})
        if "next" in links:
            return {"next_url": links["next"]}
        else:
            return {}
```

The test should now pass. We won't write more integration tests in this tutorial, but they are
strongly recommended for any connector used in production. The change on request params will cause
a fail in "test_read_a_single_page", fix this unit test is left as an exercise for the reader.

```bash
poetry run pytest unit_tests
```

We'll try reading

```bash
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

There might not be enough records in your account to trigger the pagination.

It might be easier to test pagination by forcing the connector to only fetch one record per page:

```
    _PAGE_SIZE: int = 1
```

and reading again

```bash
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

All records should be read now.

Change the \_PAGE_SIZE back to 1000:

```
    _PAGE_SIZE: int = 1000
```

In the [next section](./4-check-and-error-handling.md), we'll implement the check operation, and
improve the error handling.
