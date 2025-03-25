#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream

from .auth import OutbrainAmplifyAuthenticator


DEFAULT_END_DATE = pendulum.now()
DEFAULT_GEO_LOCATION_BREAKDOWN = "region"
DEFAULT_REPORT_GRANULARITY = "daily"


# Basic full refresh stream
class OutbrainAmplifyStream(HttpStream, ABC):
    url_base = "https://api.outbrain.com/amplify/v0.1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.json():
            total_pages = response.json().get("totalCount")
            current_page = response.json().get("count")
            if current_page < total_pages - 1:
                diff = (total_pages - current_page) - 1
                if diff < current_page + 1:
                    return {"offset": current_page + 1}
            else:
                return None
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None, **kwargs
    ) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token=next_page_token, stream_state=stream_state, **kwargs)
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield {response.json()}

    @staticmethod
    def _get_time_interval(
        start_date: Union[pendulum.datetime, str], ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if isinstance(start_date, str):
            start_date = pendulum.parse(start_date)
        end_date = pendulum.parse(ending_date) if ending_date else DEFAULT_END_DATE
        if end_date < start_date:
            raise ValueError(f"Specified start date: {start_date} is later than the end date: {end_date}")
        return start_date, end_date


class Marketers(OutbrainAmplifyStream):
    primary_key = "id"

    def __init__(self, authenticator, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "marketers.yml"

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("marketers"):
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "marketers/"


class CampaignsByMarketers(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "campaigns.yml"

    @property
    def name(self) -> str:
        return "campaigns"

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("campaigns"):
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"marketers/{stream_slice['marketer_id']}/campaigns"


# Retrieve Campaign GeoLocations.
# A new endpoint has been added which returns all targeted and excluded locations of a given campaign. It can be called in order to retrieve a campaign's geotargeting.
class CampaignsGeoLocation(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: CampaignsByMarketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("geoLocations"):
                x["campaign_id"] = stream_slice["campaign_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice['campaign_id']}/locations"


# List PromotedLinks for Campaign.
# Collection of all PromotedLinks for the specified Campaign.
class PromotedLinksForCampaigns(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: CampaignsByMarketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    @property
    def name(self) -> str:
        return "promoted_links"

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("promotedLinks"):
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice['campaign_id']}/promotedLinks"


# List PromotedLinksSequences for Campaign.
# Collection of all PromotedLinksSequences for the specified Campaign.
class PromotedLinksSequenceForCampaigns(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: CampaignsByMarketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("sequences"):
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"campaigns/{stream_slice['campaign_id']}/promotedLinksSequences"


# List Budgets for a Marketer.
# Retrieve a collection of all Budgets for the specified Marketer.
class BudgetsForMarketers(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    @property
    def name(self) -> str:
        return "budgets"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("budgets"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"marketers/{stream_slice['marketer_id']}/budgets"


# Retrieve campaigns with performance statistics for a Marketer.
# The API in this sub-section allows retrieving marketer campaigns data with performance statistics.
class PerformanceReportCampaignsByMarketers(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve periodic performance statistics for a Marketer.
# The API in this sub-section allows retrieving performance statistics by periodic breakdown at different levels: marketer, budget, campaign and promoted link.
class PerformanceReportPeriodicByMarketers(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/periodic?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&breakdown="
            + str(self.config.get("report_granularity", DEFAULT_REPORT_GRANULARITY))
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for all marketer campaigns by periodic breakdown.
# A special endpoint for retrieving periodic data by campaign breakdown. Now supports all breakdowns: daily, weekly, monthly, hourOfDay, dayOfWeek and dayOfWeekByHour.
class PerformanceReportPeriodicByMarketersCampaign(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for results in response.json().get("campaignResults"):
                for x in results.get("results"):
                    x["marketer_id"] = stream_slice["marketer_id"]
                    x["campaign_id"] = results.get("campaignId")
                    yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns/periodic?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&breakdown="
            + str(self.config.get("report_granularity", DEFAULT_REPORT_GRANULARITY))
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve periodic performance statistics by promoted link for a campaign. HERE
# A special endpoint for retrieving periodic data by promoted link breakdown for a given campaign.
class PerformanceReportPeriodicContentByPromotedLinksCampaign(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: CampaignsByMarketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    @property
    def name(self) -> str:
        return "performance_promoted_links"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("marketerId"), "campaign_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for results in response.json().get("promotedLinkResults"):
                for x in results.get("results"):
                    x["marketer_id"] = stream_slice["marketer_id"]
                    x["campaign_id"] = stream_slice["campaign_id"]
                    x["promoted_link_id"] = results.get("promotedLinkId")
                    yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns/{stream_slice['campaign_id']}/periodicContent?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&breakdown="
            + str(self.config.get("report_granularity", DEFAULT_REPORT_GRANULARITY))
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for a Marketer by publisher.
# Marketer performance statistics with breakdown by publisher with publishers that are already blocked at the marketer or campaign level.
class PerformanceReportMarketersByPublisher(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/publishers?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for all marketer campaigns by publisher
# A special endpoint for retrieving publishers data by campaign breakdown.
class PerformanceReportPublishersByCampaigns(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for fetched in response.json().get("campaignResults"):
                for x in fetched.get("results"):
                    x["marketer_id"] = stream_slice["marketer_id"]
                    x["campaign_id"] = fetched.get("campaignId")
                    yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns/publishers?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for a Marketer by platform.
# The API in this sub-section allows retrieving performance statistics by platform at different levels: marketer, budget, and campaign.
class PerformanceReportMarketersByPlatforms(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/platforms?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for all marketer campaigns by platform.
# A special endpoint for retrieving platforms data by campaign breakdown.
class PerformanceReportMarketersCampaignsByPlatforms(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for fetched in response.json().get("campaignResults"):
                for x in fetched.get("results"):
                    x["marketer_id"] = stream_slice["marketer_id"]
                    x["campaign_id"] = fetched.get("campaignId")
                    yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns/platforms?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve geo performance statistics for a Marketer.
# The API in this sub-section allows retrieving performance statistics by geographic breakdown at different levels: country, region, and subregion.
class PerformanceReportMarketersByGeoPerformance(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/geo?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&breakdown="
            + str(self.config.get("geo_location_breakdown", DEFAULT_GEO_LOCATION_BREAKDOWN))
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for all marketer campaigns by geo.
# A special endpoint for retrieving geo data by campaign breakdown.
class PerformanceReportMarketersCampaignsByGeo(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for fetched in response.json().get("campaignResults"):
                for x in fetched.get("results"):
                    x["marketer_id"] = stream_slice["marketer_id"]
                    x["campaign_id"] = fetched.get("campaignId")
                    yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/campaigns/geo?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&breakdown="
            + str(self.config.get("geo_location_breakdown", DEFAULT_GEO_LOCATION_BREAKDOWN))
            + "&limit=500"
            + "&includeVideoStats=true"
        )


# Retrieve performance statistics for a Marketer by interest.
# The API in this sub-section allows retrieving performance statistics by interest at different levels: marketer and campaign.
class PerformanceReportMarketersByInterest(OutbrainAmplifyStream, HttpSubStream):
    primary_key = None

    def __init__(self, authenticator, config, parent: Marketers, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def stream_slices(
        self, sync_mode: SyncMode.full_refresh, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )

        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(
                sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )

            for record in parent_records:
                yield {"marketer_id": record.get("id")}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("results"):
                x["marketer_id"] = stream_slice["marketer_id"]
                yield x

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
        return (
            f"reports/marketers/{stream_slice['marketer_id']}/interests?from="
            + str(stream_start.date())
            + "&to="
            + str(stream_end.date())
            + "&limit=500"
            + "&includeVideoStats=true"
        )


class IncrementalOutbrainAmplifyStream(OutbrainAmplifyStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}


# Source
class SourceOutbrainAmplify(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        url_base = OutbrainAmplifyStream.url_base
        auth = OutbrainAmplifyAuthenticator(url_base=url_base, config=config)
        try:
            auth.get_auth_header()
            marketer_stream = Marketers(authenticator=auth, config=config)
            next(marketer_stream.read_records(SyncMode.full_refresh))
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        url_base = OutbrainAmplifyStream.url_base
        auth = OutbrainAmplifyAuthenticator(url_base=url_base, config=config)
        # Basic stream marketing
        # 1. All Marketing streams
        stream = [Marketers(authenticator=auth, config=config)]

        # Campaigns Streams.
        # 1. Campaigns by marketers (implemented).
        # 2. Camapings Geo Location (implemented).
        stream.extend(
            [
                CampaignsByMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)),
                CampaignsGeoLocation(
                    authenticator=auth,
                    config=config,
                    parent=CampaignsByMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)),
                ),
            ]
        )

        # Budget for Marketers stream.
        # 1. Budget stream based on marketers id.
        (stream.extend([BudgetsForMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config))]),)

        # Promoted Links stream.
        # 1. Promoted Links stream for campaigns.
        stream.extend(
            [
                PromotedLinksForCampaigns(
                    authenticator=auth,
                    config=config,
                    parent=CampaignsByMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)),
                )
            ]
        )

        # Promoted Links Sequences stream.
        # 1. Promoted Links Sequences stream for campaigns.
        stream.extend(
            [
                PromotedLinksSequenceForCampaigns(
                    authenticator=auth,
                    config=config,
                    parent=CampaignsByMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)),
                )
            ]
        )

        # Performance Reporting.
        # 1. Streams to retrieve performance statistics.
        stream.extend(
            [
                PerformanceReportCampaignsByMarketers(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportPeriodicByMarketers(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportPeriodicByMarketersCampaign(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportPeriodicContentByPromotedLinksCampaign(
                    authenticator=auth,
                    config=config,
                    parent=CampaignsByMarketers(authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)),
                ),
                PerformanceReportMarketersByPublisher(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportPublishersByCampaigns(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportMarketersByPlatforms(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportMarketersCampaignsByPlatforms(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportMarketersByGeoPerformance(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportMarketersCampaignsByGeo(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
                PerformanceReportMarketersByInterest(
                    authenticator=auth, config=config, parent=Marketers(authenticator=auth, config=config)
                ),
            ]
        )
        return stream
