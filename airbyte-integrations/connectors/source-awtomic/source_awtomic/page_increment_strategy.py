from typing import Any, List, Mapping, Optional, Tuple
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
import urllib.parse
import json

class LastEvaluatedKeyPaginationStrategy(PageIncrement):

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        last_evaluated_key = response.json().get('LastEvaluatedKey')
        if last_evaluated_key:
            return json.dumps(last_evaluated_key)
        else:
            return None
