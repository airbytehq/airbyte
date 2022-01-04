#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import re
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from recurly import Client

DEFAULT_PRIMARY_KEY = "id"
DEFAULT_CURSOR = "updated_at"
DEFAULT_SORT_KEY = "updated_at"

BEGIN_TIME_PARAM = "begin_time"

CAMEL_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


class BaseStream(Stream):
    def __init__(self, client: Client, begin_time: str = None, **kwargs):
        super(Stream, self).__init__(**kwargs)

        self._client = client
        self.begin_time = begin_time

    @property
    def name(self):
        """
        The name of the Recurly resource. By default it converts the class name from `CamelCase` to `snake_case`.
        """
        return CAMEL_CASE_PATTERN.sub("_", type(self).__name__).lower()

    @property
    def client_method_name(self) -> str:
        """
        Returns the Recurly client method to call to retrieve the resource data.

        :return: The Recurly client method to call for the Recurly resource. For example `list_accounts` for the
                Recurly `accounts` resource
        :rtype: str
        """
        return f"list_{self.name}"

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        """
        The Recurly resource primary key. Most of the Recurly resources have `id` as a primary ID. Other Recurly
        resources have different primary key or a composite key can override this method.

        :return: The Recurly resource primary key(s)
        :rtype: Either `str`, list(str) or list(list(str))
        """
        return DEFAULT_PRIMARY_KEY

    @property
    def sort_key(self) -> str:
        """
        Sets the sort key when calling the Recurly API. Most of the Recurly API resources accept `params` dictionary
        with `sort` key. For more details:
         https://developers.recurly.com/api/v2021-02-25/#section/Getting-Started/Pagination#query-parameters

        :return: The Recurly resource sort key
        :rtype: `str`
        """
        return DEFAULT_SORT_KEY

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        """
        Returns the cursor field to be used in the `incremental` sync mode.

        By default enable the `incremental` sync mode for all resources using the `begin_time` field. Any other
        Recurly resource that either does not support `incremental` sync mode such as the `export_dates` or resources
        that use other cursor can override this method, but the `begin_time` is not a field in any of the resouce
        it is just a query parameter sent in the API request and it can be considered as an alias to the `updated_at`
        field. That's why when calling the Recurly API, the cursor field is renamed to `begin_time` by default in the
        :func:`read_records`. For more details:
            https://developers.recurly.com/api/v2021-02-25/#section/Getting-Started/Pagination#query-parameters

        :return: The cursor field(s) to be used in the `incremental` sync mode.
        :rtype: Union[str, List[str]]
        """
        return DEFAULT_CURSOR

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        The method to be called to retrieve records from the Recurly API. It uses the Recurly Python client.
        Resources having different logic (such as the `export_dates`) can override this method

        :return: Iterable of dictionaries representing the Recurly resource
        :rtype: Iterable
        """
        params = {"order": "asc", "sort": self.sort_key}

        self.begin_time = (stream_state and stream_state[self.cursor_field]) or self.begin_time

        if self.begin_time:
            params.update({BEGIN_TIME_PARAM: self.begin_time})

        # Call the Recurly client methods
        items = getattr(self._client, self.client_method_name)(params=params).items()

        for item in items:
            yield self._item_to_dict(item)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """
        Compares the current stream state cursor with the latest record cursor value and returns the latest or the most
        recent cursor value (either the current cursor value or the latest record cursor value depending which of those
        is the maximum).

        :return: The value of the new current value of the cursor
        :rtype: dict
        """
        current_updated_at = (current_stream_state or {}).get(self.cursor_field, "")
        latest_record_updated_at = latest_record[self.cursor_field].isoformat()

        return {self.cursor_field: max(latest_record_updated_at, current_updated_at)}

    def _item_to_dict(self, resource):
        """
        Recursively converts the Recurly resource object to `dict`
        """
        if isinstance(resource, dict):
            return dict((key, self._item_to_dict(value)) for key, value in resource.items())
        elif hasattr(resource, "__iter__") and not isinstance(resource, str):
            return [self._item_to_dict(value) for value in resource]
        elif hasattr(resource, "__dict__"):
            return dict([(key, self._item_to_dict(value)) for key, value in resource.__dict__.items()])
        else:
            return resource


class Accounts(BaseStream):
    pass


class AccountCouponRedemptions(BaseStream):
    pass

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        The method to be called to retrieve the accounts coupon redemptions from Recurly. To retrieve the coupon
        redemptions, a separate call to list all the accounts should be made to pass the `account_id` to the account
        coupon code redemption API call.

        :return: Iterable of dictionaries representing the Recurly resource
        :rtype: Iterable
        """
        params = {"order": "asc", "sort": self.sort_key}

        self.begin_time = (stream_state and stream_state[self.cursor_field]) or self.begin_time

        if self.begin_time:
            params.update({BEGIN_TIME_PARAM: self.begin_time})

        # Call the Recurly client methods
        accounts = self._client.list_accounts().items()
        for account in accounts:
            coupons = self._client.list_account_coupon_redemptions(account_id=account.id, params=params).items()
            for coupon in coupons:
                yield self._item_to_dict(coupon)


class Coupons(BaseStream):
    pass


class Invoices(BaseStream):
    pass


class MeasuredUnits(BaseStream):
    client_method_name = "list_measured_unit"


class Plans(BaseStream):
    pass


class Subscriptions(BaseStream):
    pass


class Transactions(BaseStream):
    pass


class ExportDates(BaseStream):
    cursor_field = []  # Disable `incremental` sync for `export_dates` Recurly API call

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        Reads the `export_dates` response from Recurly. This is a special API call different from other Recurly
        resources and hence treated differently
        """
        yield {"dates": self._client.get_export_dates().dates}
