#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import os
from abc import ABC, abstractmethod
from datetime import timezone
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pandas as pd
import pendulum
from numpy import nan

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import IncrementalMixin
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_bing_ads.base_streams import Accounts, BingAdsBaseStream
from source_bing_ads.utils import transform_bulk_datetime_format_to_rfc_3339


class BingAdsBulkStream(BingAdsBaseStream, IncrementalMixin, ABC):
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)
    cursor_field = "Modified Time"
    primary_key = "Id"
    _state = {}

    @staticmethod
    @transformer.registerCustomTransform
    def custom_transform_date_rfc3339(original_value, field_schema):
        if original_value and "format" in field_schema and field_schema["format"] == "date-time":
            transformed_value = transform_bulk_datetime_format_to_rfc_3339(original_value)
            return transformed_value
        return original_value

    @property
    @abstractmethod
    def data_scope(self) -> List[str]:
        """
        Defines scopes or types of data to download. Docs: https://learn.microsoft.com/en-us/advertising/bulk-service/datascope?view=bingads-13
        """

    @property
    @abstractmethod
    def download_entities(self) -> List[str]:
        """
        Defines the entities that should be downloaded. Docs: https://learn.microsoft.com/en-us/advertising/bulk-service/downloadentity?view=bingads-13
        """

    def stream_slices(
        self,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        accounts = Accounts(self.client, self.config)
        for _slice in accounts.stream_slices():
            for account in accounts.read_records(SyncMode.full_refresh, _slice):
                yield {"account_id": account["Id"], "customer_id": account["ParentCustomerId"]}

    @property
    def state(self) -> Mapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        # if key 'Account Id' exists, so we receive a record that should be parsed to state
        # otherwise state object from connection state was received
        account_id = value.get("Account Id")

        if account_id and value[self.cursor_field]:
            current_state_value = self._state.get(str(value["Account Id"]), {}).get(self.cursor_field, "")
            record_state_value = transform_bulk_datetime_format_to_rfc_3339(value[self.cursor_field])
            new_state_value = max(current_state_value, record_state_value)
            self._state.update({str(value["Account Id"]): {self.cursor_field: new_state_value}})
        else:
            self._state.update(value)

    def get_start_date(self, stream_state: Mapping[str, Any] = None, account_id: str = None) -> Optional[pendulum.DateTime]:
        """
        The start_date in the query can only be specified if it is within a period of up to 30 days from today.
        """
        min_available_date = pendulum.now().subtract(days=30).astimezone(tz=timezone.utc)
        start_date = self.client.reports_start_date
        if stream_state.get(account_id, {}).get(self.cursor_field):
            start_date = pendulum.parse(stream_state[account_id][self.cursor_field])
        return start_date if start_date and start_date > min_available_date else None

    def read_records(
        self,
        sync_mode: SyncMode,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        **kwargs: Mapping[str, Any],
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        account_id = str(stream_slice.get("account_id")) if stream_slice else None
        customer_id = str(stream_slice.get("customer_id")) if stream_slice else None

        report_file_path = self.client.get_bulk_entity(
            data_scope=self.data_scope,
            download_entities=self.download_entities,
            customer_id=customer_id,
            account_id=account_id,
            start_date=self.get_start_date(stream_state, account_id),
        )
        for record in self.read_with_chunks(report_file_path):
            record = self.transform(record, stream_slice)
            yield record
            self.state = record

    def read_with_chunks(self, path: str, chunk_size: int = 1024) -> Iterable[Tuple[int, Mapping[str, Any]]]:
        try:
            with open(path, "r") as data:
                chunks = pd.read_csv(data, chunksize=chunk_size, iterator=True, dialect="unix", dtype=object)
                for chunk in chunks:
                    chunk = chunk.replace({nan: None}).to_dict(orient="records")
                    for row in chunk:
                        if row.get("Type") not in ("Format Version", "Account"):
                            yield row
        except pd.errors.EmptyDataError as e:
            self.logger.info(f"Empty data received. {e}")
        except IOError as ioe:
            self.logger.fatal(
                f"The IO/Error occurred while reading tmp data. Called: {path}. Stream: {self.name}",
            )
            raise ioe
        finally:
            # remove binary tmp file, after data is read
            os.remove(path)

    def transform(self, record: MutableMapping[str, Any], stream_slice: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        """
        Bing Ads Bulk API returns all available properties for all entities.
        This method filter out only available properties.
        """
        actual_record = {key: value for key, value in record.items() if key in self.get_json_schema()["properties"].keys()}
        actual_record["Account Id"] = stream_slice.get("account_id")
        return actual_record


class AppInstallAds(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AppInstallAds"]


class AppInstallAdLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/app-install-ad-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AppInstallAdLabels"]


class Labels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["Labels"]


class KeywordLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/keyword-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["KeywordLabels"]


class Keywords(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/keyword?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["Keywords"]


class CampaignLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/campaign-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["CampaignLabels"]


class AdGroupLabels(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/ad-group-label?view=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["AdGroupLabels"]


class Budget(BingAdsBulkStream):
    """
    https://learn.microsoft.com/en-us/advertising/bulk-service/budget?view=bingads-13&viewFallbackFrom=bingads-13
    """

    data_scope = ["EntityData"]
    download_entities = ["Budgets"]
