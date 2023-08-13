from typing import Any, Iterable, Mapping
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from typing import Any, List
import requests

class CustomExtractor(RecordExtractor):
    
    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:

        extracted=[]
        print(response.json())
        for cat in response.json()['categories']:
            extracted.append({"name": cat})
        return extracted