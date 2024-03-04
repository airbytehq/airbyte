from airbyte_cdk.sources.streams.http import HttpStream
import urllib.parse
import json
import requests

class CustomHttpStream(HttpStream):

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Extract the 'LastEvaluatedKey' from the response
        response_json = response.json()
        last_evaluated_key = response_json.get('LastEvaluatedKey')
        if last_evaluated_key:
            return {'lastEvaluatedKey': last_evaluated_key}
        else:
            return None

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> MutableMapping[str, Any]:
        # Add the 'lastEvaluatedKey' to the request parameters
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if next_page_token:
            last_evaluated_key = next_page_token.get('lastEvaluatedKey')
            if last_evaluated_key:
                # Encode the 'lastEvaluatedKey' and add it to the request parameters
                encoded_key = urllib.parse.quote(json.dumps(last_evaluated_key))
                params['lastEvaluatedKey'] = encoded_key
        return params