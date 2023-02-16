import pendulum

from airbyte_cdk.sources.abstract_source import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.models import SyncMode

from typing import Any, List, Mapping, Tuple

from .streams import SalesHistory, SalesCommissions, SalesPriceDetails, SalesUsers

from .oauth import HotmartOauth2Authenticator

# Source
class SourceHotmart(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        client_id, client_secret, refresh_token = config["client_id"], config["client_secret"], config["token"]
        auth = HotmartOauth2Authenticator(client_id, client_secret, refresh_token)

        try:
            args = {"authenticator": auth, "start_date": pendulum.parse(config["start_date"]).int_timestamp}

            sales_history_stream = SalesHistory(**args)
            next(sales_history_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except Exception as e:
            logger.debug(e)
            return False, f"Please check that you entered the Hotmart Credentials correctly. Exception: {repr(e)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        client_id, client_secret, refresh_token = config["client_id"], config["client_secret"], config["token"]
        auth = HotmartOauth2Authenticator(client_id, client_secret, refresh_token)

        args = {"authenticator": auth, "start_date": pendulum.parse(config["start_date"]).int_timestamp}

        if "slice_range" in config:
            args["slice_range"] = int(config["slice_range"])

        return [SalesHistory(**args), SalesCommissions(**args), SalesPriceDetails(**args), SalesUsers(**args)]
