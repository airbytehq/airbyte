#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

from pendulum import parse, today

from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream

from .google_ads import GoogleAds
from .models import CustomerModel
from .streams import (
    CustomerClient,
)
from .utils import logger


class SourceGoogleAds(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    # Raise exceptions on missing streams
    raise_exception_on_missing_stream = True

    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any]):
        if config.get("end_date") == "":
            config.pop("end_date")
        if "customer_id" in config:
            config["customer_ids"] = config["customer_id"].split(",")
            config.pop("customer_id")

        return config

    @staticmethod
    def get_credentials(config: Mapping[str, Any]) -> MutableMapping[str, Any]:
        credentials = config["credentials"]
        # use_proto_plus is set to True, because setting to False returned wrong value types, which breaks the backward compatibility.
        # For more info read the related PR's description: https://github.com/airbytehq/airbyte/pull/9996
        credentials.update(use_proto_plus=True)
        return credentials

    @staticmethod
    def get_incremental_stream_config(google_api: GoogleAds, config: Mapping[str, Any], customers: List[CustomerModel]):
        # date range is mandatory parameter for incremental streams, so default start day is used
        start_date = config.get("start_date", today().subtract(years=2).to_date_string())

        end_date = config.get("end_date")
        # check if end_date is not in the future, set to today if it is
        end_date = min(today(), parse(end_date)) if end_date else today()
        end_date = end_date.to_date_string()

        incremental_stream_config = dict(
            api=google_api,
            customers=customers,
            conversion_window_days=config.get("conversion_window_days", 0),
            start_date=start_date,
            end_date=end_date,
        )
        return incremental_stream_config

    def get_all_accounts(self, google_api: GoogleAds, customers: List[CustomerModel], customer_status_filter: List[str]) -> List[str]:
        customer_clients_stream = CustomerClient(api=google_api, customers=customers, customer_status_filter=customer_status_filter)
        for slice in customer_clients_stream.stream_slices():
            for record in customer_clients_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=slice):
                yield record

    def _get_all_connected_accounts(
        self, google_api: GoogleAds, customer_status_filter: List[str]
    ) -> Iterable[Iterable[Mapping[str, Any]]]:
        customer_ids = [customer_id for customer_id in google_api.get_accessible_accounts()]
        dummy_customers = [CustomerModel(id=_id, login_customer_id=_id) for _id in customer_ids]

        yield from self.get_all_accounts(google_api, dummy_customers, customer_status_filter)

    def get_customers(self, google_api: GoogleAds, config: Mapping[str, Any]) -> List[CustomerModel]:
        customer_status_filter = config.get("customer_status_filter", [])
        accounts = self._get_all_connected_accounts(google_api, customer_status_filter)

        # filter only selected accounts
        if config.get("customer_ids"):
            return CustomerModel.from_accounts_by_id(accounts, config["customer_ids"])

        # all unique accounts
        return CustomerModel.from_accounts(accounts)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self._validate_and_transform(config)
        google_api = GoogleAds(credentials=self.get_credentials(config))

        customers = self.get_customers(google_api, config)
        logger.info(f"Found {len(customers)} customers: {[customer.id for customer in customers]}")

        non_manager_accounts = [customer for customer in customers if not customer.is_manager_account]
        default_config = dict(api=google_api, customers=customers)
        incremental_config = self.get_incremental_stream_config(google_api, config, customers)
        non_manager_incremental_config = self.get_incremental_stream_config(google_api, config, non_manager_accounts)

        streams = super().streams(config=config)
        return streams
