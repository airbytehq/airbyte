from typing import Optional, Union, List, Mapping, Any, Iterable

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from recurly import Client


class BaseRecurlyStream(Stream):
    def __init__(self, client: Client):
        super(Stream, self).__init__()

        self._client = client

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "id"

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        items = getattr(self._client, f"list_{self.name}")().items()
        for item in items:
            yield self.__item_to_dict(item)

    def __item_to_dict(self, resource):
        if isinstance(resource, dict):
            return dict((key, self.__item_to_dict(value)) for key, value in resource.items())
        elif hasattr(resource, "__iter__") and not isinstance(resource, str):
            return [self.__item_to_dict(value) for value in resource]
        elif hasattr(resource, "__dict__"):
            return dict([(key, self.__item_to_dict(value)) for key, value in resource.__dict__.items()])
        else:
            return resource


class RecurlyAccountsStream(BaseRecurlyStream):
    name = "accounts"


class RecurlyCouponsStream(BaseRecurlyStream):
    name = "coupons"


class RecurlyInvoicesStream(BaseRecurlyStream):
    name = "invoices"


class RecurlyMeasuredUnitsStream(BaseRecurlyStream):
    name = "measured_units"


class RecurlyPlansStream(BaseRecurlyStream):
    name = "plans"


class RecurlySubscriptionsStream(BaseRecurlyStream):
    name = "subscriptions"


class RecurlyTransactionsStream(BaseRecurlyStream):
    name = "transactions"


class RecurlyExportDatesStream(BaseRecurlyStream):
    name = "export_dates"

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        """
        Reads the `export_dates` response from Recurly. This is a special API call different from other Recurly
        resources and hence treated differently
        """
        yield {"dates": self._client.get_export_dates().dates}
