import requests
from typing import Any, Mapping, Tuple, List
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from .stream_events import PurchasedEvents, PackRevealEvents

class SourceGraffle(AbstractSource):

    def check_connection(self, _, config) -> Tuple[bool, str]:
        url_param = f"api/company/{config['company_id']}/search"
        url = f"https://prod-main-net-dashboard-api.azurewebsites.net/{url_param}"
        response = requests.get(url)
        try:
            _ = response.json()
            return True, "accepted"
        except:
            return False, "error"


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            PurchasedEvents(config, "A.30cf5dcf6ea8d379.AeraPack.Purchased"),
            PackRevealEvents(config, "A.30cf5dcf6ea8d379.AeraPack.PackReveal"),
        ]
