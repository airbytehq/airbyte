#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from source_active_campaign.auth import TokenAuthenticator
from source_active_campaign.proxy_stream import ProxyStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.models import SyncMode

CONFIG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SERVICE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# Basic full refresh stream
class ActiveCampaignStream(ProxyStream, ABC):
    pagination_limit = 100
    primary_key = "id"
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization,
    )

    def __init__(self, authenticator: TokenAuthenticator = None, account_name: str = None, proxy_url: str = None):
        super().__init__(authenticator=authenticator, proxy_url=proxy_url)
        self.account_name = account_name
        self.current_offset = 0

    @property
    @abstractmethod
    def resource_name(self) -> str:
        return None

    @property
    def data_key(self) -> str | None:
        return None

    @property
    def url_base(self) -> str:
        return f"https://{self.account_name}.api-us1.com/api/3/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        objects_count = len(data[self.resource_name])
        if objects_count < self.pagination_limit:
            return None

        self.current_offset += self.pagination_limit
        return {"offset": self.current_offset}

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return self.resource_name

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            "limit": self.pagination_limit,
            "offset": next_page_token["offset"] if next_page_token else 0,
        }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data_key = self.resource_name
        if self.data_key is not None:
            data_key = self.data_key
        yield from response.json()[data_key]


class DateTimeStream(ActiveCampaignStream):
    def __init__(
        self,
        authenticator: TokenAuthenticator,
        account_name: str,
        datetime_from: datetime | None,
        datetime_to: datetime | None,
        proxy_url: str = None,
    ):
        super().__init__(
            authenticator=authenticator,
            account_name=account_name,
            proxy_url=proxy_url,
        )
        self.datetime_from = datetime_from
        self.datetime_to = datetime_to

    @staticmethod
    def datetime_to_str(dt: datetime) -> str:
        return dt.strftime(SERVICE_DATETIME_FORMAT)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            **super().request_params(
                stream_state,
                stream_slice,
                next_page_token,
            ),
        }
        if self.datetime_from:
            params.update(
                {
                    "filters[created_after]": self.datetime_to_str(self.datetime_from),
                    "filters[updated_after]": self.datetime_to_str(self.datetime_from),
                }
            )
        if self.datetime_to:
            params.update(
                {
                    "filters[created_berore]": self.datetime_to_str(self.datetime_to),
                    "filters[updated_before]": self.datetime_to_str(self.datetime_to),
                }
            )
        return params


class Accounts(ActiveCampaignStream):
    resource_name = "accounts"


class AccountContactAssociation(ActiveCampaignStream):
    resource_name = "accountContacts"


class CustomAccountFields(ActiveCampaignStream):
    resource_name = "accountCustomFieldMeta"


class CustomAccountFieldValues(ActiveCampaignStream):
    resource_name = "accountCustomFieldData"


class Addresses(ActiveCampaignStream):
    resource_name = "addresses"


class Automations(ActiveCampaignStream):
    resource_name = "automations"


class Brandings(ActiveCampaignStream):
    resource_name = "brandings"


class Messages(ActiveCampaignStream):
    resource_name = "messages"


class Contacts(DateTimeStream):
    resource_name = "contacts"


class ContactAutomations(ActiveCampaignStream):
    resource_name = "contactAutomations"


class CustomFields(ActiveCampaignStream):
    resource_name = "fields"


class CustomFieldsValues(ActiveCampaignStream):
    resource_name = "fieldValues"


class EmailActivities(ActiveCampaignStream):
    resource_name = "emailActivities"


class DealGroups(ActiveCampaignStream):
    resource_name = "dealGroups"


class DealStages(ActiveCampaignStream):
    resource_name = "dealStages"


class DealCustomFields(ActiveCampaignStream):
    resource_name = "dealCustomFieldMeta"


class DealCustomFieldValues(ActiveCampaignStream):
    resource_name = "dealCustomFieldData"


class ContactDeals(ActiveCampaignStream):
    resource_name = "contactDeals"


class DealRoles(ActiveCampaignStream):
    resource_name = "dealRoles"


class Connections(ActiveCampaignStream):
    resource_name = "connections"


class EcomCustomers(ActiveCampaignStream):
    resource_name = "ecomCustomers"


class EcomOrders(ActiveCampaignStream):
    resource_name = "ecomOrders"


class EcomOrderProducts(ActiveCampaignStream):
    resource_name = "ecomOrderProducts"


class Forms(ActiveCampaignStream):
    resource_name = "forms"


class CalendarFeeds(ActiveCampaignStream):
    resource_name = "calendars"


class Campaigns(ActiveCampaignStream):
    resource_name = "campaigns"


class Deals(DateTimeStream):
    resource_name = "deals"


class Lists(ActiveCampaignStream):
    resource_name = "lists"


class Notes(ActiveCampaignStream):
    resource_name = "notes"


class SavedResponses(ActiveCampaignStream):
    resource_name = "savedResponses"


class Scores(ActiveCampaignStream):
    resource_name = "scores"


class Segments(ActiveCampaignStream):
    resource_name = "segments"


class SiteTrackingDomains(ActiveCampaignStream):
    primary_key = None
    resource_name = "siteTrackingDomains"


class Tags(ActiveCampaignStream):
    resource_name = "tags"


class DealTasks(ActiveCampaignStream):
    resource_name = "dealTasks"


class TaskOutcomes(ActiveCampaignStream):
    resource_name = "taskOutcomes"


class DealTaskTypes(ActiveCampaignStream):
    resource_name = "dealTasktypes"


class TaskTypeOutcomeRels(ActiveCampaignStream):
    resource_name = "tasktypeOutcomeRels"


class Templates(ActiveCampaignStream):
    resource_name = "templates"


class Users(ActiveCampaignStream):
    resource_name = "users"


class Groups(ActiveCampaignStream):
    resource_name = "groups"


class GroupLimits(ActiveCampaignStream):
    resource_name = "groupLimits"


class Webhooks(ActiveCampaignStream):
    resource_name = "webhooks"


# Source
class SourceActiveCampaign(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        config = self.transform_config(config)
        authenticator = TokenAuthenticator(token=config["token"])
        print(config.get("proxy_url"))
        test_stream = Accounts(
            authenticator=authenticator,
            account_name=config["account_name"],
            proxy_url=config.get("proxy_url"),
        )
        print(test_stream._session.get("https://api64.ipify.org?format=json").json())
        next(test_stream.read_records(sync_mode=SyncMode))
        return True, None

    @staticmethod
    def check_datetime_range_abnormal(datetime_from: datetime, datetime_to: datetime) -> None:
        if bool(datetime_from) ^ bool(datetime_to):
            raise ValueError("You must specify both 'datetime_from' and 'datetime_to'.")
        if datetime_from and datetime_to:
            if datetime_from > datetime_to:
                raise ValueError("'datetime_from' is more than datetime_to.")
            if datetime_to > datetime.now():
                raise ValueError("'datetime_to' is more than now.")

    def transform_config(self, config: dict[str, Any]) -> dict[str, Any]:
        if not config.get("proxy_url"):
            config["proxy_url"] = None

        datetime_range: dict[str, Any] = config.get(
            "datetime_range",
            {"datetime_range_type": "all"},
        )
        datetime_range_type = datetime_range["datetime_range_type"]
        if datetime_range_type == "last_days_range":
            should_load_today = datetime_range.get("should_load_today", False)
            last_days_count: int = datetime_range.get("last_days_count")
            today_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            datetime_from = today_datetime - timedelta(days=last_days_count)
            if should_load_today:
                datetime_to = today_datetime
            else:
                datetime_to = today_datetime - timedelta(days=1)
        elif datetime_range_type == "custom_datetime_range":
            datetime_from = datetime.strptime(
                datetime_range.get("datetime_from"),
                CONFIG_DATETIME_FORMAT,
            )
            datetime_to = datetime.strptime(
                datetime_range.get("datetime_to"),
                CONFIG_DATETIME_FORMAT,
            )
        elif datetime_range_type == "all":
            datetime_from = None
            datetime_to = None
        else:
            raise ValueError(f"Incompatible datetime_range_type: '{datetime_range_type}'.")
        self.check_datetime_range_abnormal(datetime_from=datetime_from, datetime_to=datetime_to)
        config["datetime_from"] = datetime_from
        config["datetime_to"] = datetime_to
        return config

    def streams(self, config: dict[str, Any]) -> List[Stream]:
        config = self.transform_config(config)
        authenticator = TokenAuthenticator(token=config["token"])
        shared_kwargs: dict[str, Any] = dict(
            authenticator=authenticator, account_name=config["account_name"], proxy_url=config.get("proxy_url")
        )
        base_streams = [
            Accounts(**shared_kwargs),
            AccountContactAssociation(**shared_kwargs),
            CustomAccountFields(**shared_kwargs),
            CustomAccountFieldValues(**shared_kwargs),
            Addresses(**shared_kwargs),
            Automations(**shared_kwargs),
            Brandings(**shared_kwargs),
            Messages(**shared_kwargs),
            ContactAutomations(**shared_kwargs),
            CustomFields(**shared_kwargs),
            CustomFieldsValues(**shared_kwargs),
            EmailActivities(**shared_kwargs),
            DealGroups(**shared_kwargs),
            DealStages(**shared_kwargs),
            DealCustomFields(**shared_kwargs),
            DealCustomFieldValues(**shared_kwargs),
            ContactDeals(**shared_kwargs),
            DealRoles(**shared_kwargs),
            Connections(**shared_kwargs),
            EcomCustomers(**shared_kwargs),
            EcomOrders(**shared_kwargs),
            EcomOrderProducts(**shared_kwargs),
            Forms(**shared_kwargs),
            CalendarFeeds(**shared_kwargs),
            Campaigns(**shared_kwargs),
            Lists(**shared_kwargs),
            Notes(**shared_kwargs),
            SavedResponses(**shared_kwargs),
            Scores(**shared_kwargs),
            Segments(**shared_kwargs),
            SiteTrackingDomains(**shared_kwargs),
            Tags(**shared_kwargs),
            DealTasks(**shared_kwargs),
            TaskOutcomes(**shared_kwargs),
            DealTaskTypes(**shared_kwargs),
            TaskTypeOutcomeRels(**shared_kwargs),
            Templates(**shared_kwargs),
            Users(**shared_kwargs),
            Groups(**shared_kwargs),
            GroupLimits(**shared_kwargs),
            Webhooks(**shared_kwargs),
        ]
        datetime_stream_shared_kwargs: dict[str, Any] = {
            **shared_kwargs,
            "datetime_from": config.get("datetime_from"),
            "datetime_to": config.get("datetime_to"),
        }
        datetime_streams: list[Stream] = [
            Contacts(**datetime_stream_shared_kwargs),
            Deals(**datetime_stream_shared_kwargs),
        ]
        return base_streams + datetime_streams
