#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import datetime
from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Type

import pendulum
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    AuthSpecification,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    DestinationSyncMode,
    OAuth2Specification,
    Status,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.config import BaseConfig
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import (
    InternalConfig,
    ResourceSchemaLoader,
)
from pydantic import BaseModel, Field
from source_facebook_marketing.api import API
from source_facebook_marketing.streams import (
    AdCreatives,
    Ads,
    AdSets,
    AdsInsights,
    AdsInsightsActionType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
    Campaigns,
    Videos,
)

logger = logging.getLogger("airbyte")


class InsightConfig(BaseModel):

    name: str = Field(description="The name value of insight")

    fields: Optional[List[str]] = Field(description="A list of chosen fields for fields parameter", default=[])

    breakdowns: Optional[List[str]] = Field(description="A list of chosen breakdowns for breakdowns", default=[])

    action_breakdowns: Optional[List[str]] = Field(description="A list of chosen action_breakdowns for action_breakdowns", default=[])


class ConnectorConfig(BaseConfig):
    class Config:
        title = "Source Facebook Marketing"

    start_date: datetime = Field(
        title="Start Date",
        order=0,
        description="The date from which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-25T00:00:00Z"],
    )

    end_date: Optional[datetime] = Field(
        title="End Date",
        order=1,
        description="The date until which you'd like to replicate data for AdCreatives and AdInsights APIs, in the format YYYY-MM-DDT00:00:00Z. All data generated between start_date and this date will be replicated. Not setting this option will result in always syncing the latest data.",
        pattern="^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        examples=["2017-01-26T00:00:00Z"],
        default_factory=pendulum.now,
    )

    account_id: str = Field(
        title="Account ID",
        order=2,
        description="The Facebook Ad account ID to use when pulling data from the Facebook Marketing API.",
        examples=["111111111111111"],
    )

    access_token: str = Field(
        title="Access Token",
        order=3,
        description='The value of the access token generated. See the <a href="https://docs.airbyte.io/integrations/sources/facebook-marketing">docs</a> for more information',
        airbyte_secret=True,
    )

    include_deleted: bool = Field(
        title="Include Deleted",
        order=4,
        default=False,
        description="Include data from deleted Campaigns, Ads, and AdSets",
    )

    fetch_thumbnail_images: bool = Field(
        title="Fetch Thumbnail Images",
        order=5,
        default=False,
        description="In each Ad Creative, fetch the thumbnail_url and store the result in thumbnail_data_url",
    )

    custom_insights: Optional[List[InsightConfig]] = Field(
        title="Custom Insights",
        order=6,
        description="A list which contains insights entries, each entry must have a name and can contains fields, breakdowns or action_breakdowns)",
    )


class SourceFacebookMarketing(AbstractSource):
    def check_connection(self, logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        ok = False
        error_msg = None

        try:
            config = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
            api = API(account_id=config.account_id, access_token=config.access_token)
            logger.info(f"Select account {api.account}")
            ok = True
        except Exception as exc:
            error_msg = repr(exc)

        return ok, error_msg

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config: ConnectorConfig = ConnectorConfig.parse_obj(config)  # FIXME: this will be not need after we fix CDK
        api = API(account_id=config.account_id, access_token=config.access_token)

        insights_args = dict(
            api=api,
            start_date=config.start_date,
            end_date=config.end_date,
        )

        streams = [
            Campaigns(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdSets(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            Ads(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
            AdCreatives(api=api, fetch_thumbnail_images=config.fetch_thumbnail_images),
            AdsInsights(**insights_args),
            AdsInsightsAgeAndGender(**insights_args),
            AdsInsightsCountry(**insights_args),
            AdsInsightsRegion(**insights_args),
            AdsInsightsDma(**insights_args),
            AdsInsightsPlatformAndDevice(**insights_args),
            AdsInsightsActionType(**insights_args),
            Videos(api=api, start_date=config.start_date, end_date=config.end_date, include_deleted=config.include_deleted),
        ]

        return self._update_insights_streams(insights=config.custom_insights, args=insights_args, streams=streams)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Implements the Check Connection operation from the Airbyte Specification. See https://docs.airbyte.io/architecture/airbyte-specification."""
        try:
            check_succeeded, error = self.check_connection(logger, config)
            if not check_succeeded:
                return AirbyteConnectionStatus(status=Status.FAILED, message=repr(error))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=repr(e))

        # FIXME: replace validation with schema
        self._check_custom_insights_entries(config.get("custom_insights", []))

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            changelogUrl="https://docs.airbyte.io/integrations/sources/facebook-marketing",
            supportsIncremental=True,
            supported_destination_sync_modes=[DestinationSyncMode.append],
            connectionSpecification=ConnectorConfig.schema(),
            authSpecification=AuthSpecification(
                auth_type="oauth2.0",
                oauth2Specification=OAuth2Specification(
                    rootObject=[], oauthFlowInitParameters=[], oauthFlowOutputParameters=[["access_token"]]
                ),
            ),
        )

    def _update_insights_streams(self, insights, args, streams) -> List[Type[Stream]]:
        """Update method, if insights have values returns streams replacing the
        default insights streams else returns streams

        """
        if not insights:
            return streams

        insights_custom_streams = list()

        for insight in insights:
            args["name"] = f"Custom{insight.name}"
            args["fields"] = list(set(insight.fields))
            args["breakdowns"] = list(set(insight.breakdowns))
            args["action_breakdowns"] = list(set(insight.action_breakdowns))
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams

    def _check_custom_insights_entries(self, insights: List[Mapping[str, Any]]):

        loader = ResourceSchemaLoader(package_name_from_class(self.__class__))
        default_fields = list(loader.get_schema("ads_insights").get("properties", {}).keys())
        default_breakdowns = list(loader.get_schema("ads_insights_breakdowns").get("properties", {}).keys())
        default_action_breakdowns = list(loader.get_schema("ads_insights_action_breakdowns").get("properties", {}).keys())

        for insight in insights:
            if insight.get("fields"):
                value_checked, value = self._check_values(default_fields, insight["fields"])
                if not value_checked:
                    message = f"{value} is not a valid field name"
                    raise Exception("Config validation error: " + message) from None
            if insight.get("breakdowns"):
                value_checked, value = self._check_values(default_breakdowns, insight["breakdowns"])
                if not value_checked:
                    message = f"{value} is not a valid breakdown name"
                    raise Exception("Config validation error: " + message) from None
            if insight.get("action_breakdowns"):
                value_checked, value = self._check_values(default_action_breakdowns, insight["action_breakdowns"])
                if not value_checked:
                    message = f"{value} is not a valid action_breakdown name"
                    raise Exception("Config validation error: " + message) from None

        return True

    def _check_values(self, default_value: List[str], custom_value: List[str]) -> Tuple[bool, Any]:
        for e in custom_value:
            if e not in default_value:
                logger.error(f"{e} does not appear in {default_value}")
                return False, e

        return True, None

    def _read_incremental(
        self,
        logger: AirbyteLogger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        """We override this method because we need to inject new state handling.
        Old way:
            pass stream_state in read_records and other methods
            call stream_state = stream_instance.get_updated_state(stream_state, record_data) for each record
        New way:
            stream_instance.state = stream_state
            call stream_instance.state when we want to dump state message

        :param logger:
        :param stream_instance:
        :param configured_stream:
        :param connector_state:
        :param internal_config:
        :return:
        """
        if not hasattr(stream_instance, "state"):
            yield from super()._read_incremental(logger, stream_instance, configured_stream, connector_state, internal_config)
            return

        stream_name = configured_stream.stream.name
        stream_state = connector_state.get(stream_name, {})
        if stream_state:
            logger.info(f"Setting state of {stream_name} stream to {stream_state}")
            stream_instance.state = stream_state

        slices = stream_instance.stream_slices(
            cursor_field=configured_stream.cursor_field, sync_mode=SyncMode.incremental, stream_state=stream_state
        )
        total_records_counter = 0
        for _slice in slices:
            records = stream_instance.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=_slice,
                stream_state=stream_state,
                cursor_field=configured_stream.cursor_field or None,
            )
            for record_counter, record_data in enumerate(records, start=1):
                yield self._as_airbyte_record(stream_name, record_data)
                checkpoint_interval = stream_instance.state_checkpoint_interval
                if checkpoint_interval and record_counter % checkpoint_interval == 0:
                    yield self._checkpoint_state(stream_name, stream_instance.state, connector_state, logger)

                total_records_counter += 1
                # This functionality should ideally live outside of this method
                # but since state is managed inside this method, we keep track
                # of it here.
                if self._limit_reached(internal_config, total_records_counter):
                    # Break from slice loop to save state and exit from _read_incremental function.
                    break

            yield self._checkpoint_state(stream_name, stream_instance.state, connector_state, logger)
            if self._limit_reached(internal_config, total_records_counter):
                return
