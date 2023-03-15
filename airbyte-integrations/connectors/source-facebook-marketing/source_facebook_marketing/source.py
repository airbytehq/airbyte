#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, List, Mapping, Optional, Tuple, Type, Iterator

from airbyte_cdk.models import Type as MessageType

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    Level,
    Status,
    SyncMode,
)

import pendulum
import requests
from airbyte_cdk.models import AuthSpecification, ConnectorSpecification, DestinationSyncMode, OAuth2Specification
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from source_facebook_marketing.api import API
from source_facebook_marketing.spec import ConnectorConfig, InsightConfig
from source_facebook_marketing.streams import (
    Activities,
    AdAccount,
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
    CustomConversions,
    Images,
    Videos,
)

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config

from .utils import validate_end_date, validate_start_date

logger = logging.getLogger("airbyte")


class SourceFacebookMarketing(AbstractSource):
    def _read_incremental(
        self,
        logger: logging.Logger,
        stream_instance: Stream,
        configured_stream: ConfiguredAirbyteStream,
        state_manager: ConnectorStateManager,
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        """Read stream using incremental algorithm

        :param logger:
        :param stream_instance:
        :param configured_stream:
        :param state_manager:
        :param internal_config:
        :return:
        """
        stream_name = configured_stream.stream.name
        stream_state = state_manager.get_stream_state(stream_name, stream_instance.namespace)

        if stream_state and "state" in dir(stream_instance):
            stream_instance.state = stream_state
            logger.info(f"Setting state of {stream_name} stream to {stream_state}")

        slices = stream_instance.stream_slices(
            cursor_field=configured_stream.cursor_field,
            sync_mode=SyncMode.incremental,
            stream_state=stream_state,
        )
        logger.debug(f"Processing stream slices for {stream_name} (sync_mode: incremental)", extra={"stream_slices": slices})

        total_records_counter = 0
        has_slices = False
        for _slice in slices:
            has_slices = True
            if logger.isEnabledFor(logging.DEBUG):
                yield AirbyteMessage(
                    type=MessageType.LOG,
                    log=AirbyteLogMessage(level=Level.INFO, message=f"{self.SLICE_LOG_PREFIX}{json.dumps(_slice, default=str)}"),
                )
            records = stream_instance.read_records(
                sync_mode=SyncMode.incremental,
                stream_slice=_slice,
                stream_state=stream_state,
                cursor_field=configured_stream.cursor_field or None,
            )
            record_counter = 0
            for message_counter, record_data_or_message in enumerate(records, start=1):
                message = self._get_message(record_data_or_message, stream_instance)
                yield message
                if message.type == MessageType.RECORD:
                    record = message.record
                    account_id = stream_instance._api.account._data["account_id"]
                    stream_state = stream_instance.get_updated_state(stream_state, record.data, account_id=account_id)
                    checkpoint_interval = stream_instance.state_checkpoint_interval
                    record_counter += 1
                    if checkpoint_interval and record_counter % checkpoint_interval == 0:
                        yield self._checkpoint_state(stream_instance, stream_state, state_manager)

                    total_records_counter += 1
                    # This functionality should ideally live outside of this method
                    # but since state is managed inside this method, we keep track
                    # of it here.
                    if self._limit_reached(internal_config, total_records_counter):
                        # Break from slice loop to save state and exit from _read_incremental function.
                        break

            yield self._checkpoint_state(stream_instance, stream_state, state_manager)
            if self._limit_reached(internal_config, total_records_counter):
                return

        if not has_slices:
            # Safety net to ensure we always emit at least one state message even if there are no slices
            checkpoint = self._checkpoint_state(stream_instance, stream_state, state_manager)
            yield checkpoint

    def _validate_and_transform(self, config: Mapping[str, Any]):
        if config.get("end_date") == "":
            config.pop("end_date")
        config = ConnectorConfig.parse_obj(config)
        config.start_date = pendulum.instance(config.start_date)
        config.end_date = pendulum.instance(config.end_date)
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param logger: source logger
        :param config:  the user-input config object conforming to the connector's spec.json
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        config = self._validate_and_transform(config)
        if config.end_date < config.start_date:
            return False, "end_date must be equal or after start_date."

        try:
            api = API(account_id=config.account_id, access_token=config.access_token, google_service_account=config.google_service_account)
            logger.info(f"{len(api.accounts)} accounts selected: {sorted([int(account.get('account_id')) for account in api.accounts], reverse=True)}")
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of the stream instances
        """
        config = self._validate_and_transform(config)
        config.start_date = validate_start_date(config.start_date)
        config.end_date = validate_end_date(config.start_date, config.end_date)

        api = API(account_id=config.account_id, access_token=config.access_token, google_service_account=config.google_service_account)

        insights_args = dict(
            api=api, start_date=config.start_date, end_date=config.end_date, insights_lookback_window=config.insights_lookback_window
        )
        streams = [
            AdAccount(api=api),
            AdSets(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Ads(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            AdCreatives(
                api=api,
                fetch_thumbnail_images=config.fetch_thumbnail_images,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            AdsInsights(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsAgeAndGender(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsCountry(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsRegion(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsDma(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsPlatformAndDevice(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            AdsInsightsActionType(page_size=config.page_size, max_batch_size=config.max_batch_size, **insights_args),
            Campaigns(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            CustomConversions(
                api=api,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Images(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Videos(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
            Activities(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
                max_batch_size=config.max_batch_size,
            ),
        ]

        return self._update_insights_streams(insights=config.custom_insights, default_args=insights_args, streams=streams)

    def spec(self, *args, **kwargs) -> ConnectorSpecification:
        """Returns the spec for this integration.
        The spec is a JSON-Schema object describing the required configurations
        (e.g: username and password) required to run this integration.
        """
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/facebook-marketing",
            changelogUrl="https://docs.airbyte.com/integrations/sources/facebook-marketing",
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

    def _update_insights_streams(self, insights: List[InsightConfig], default_args, streams) -> List[Type[Stream]]:
        """Update method, if insights have values returns streams replacing the
        default insights streams else returns streams
        """
        if not insights:
            return streams

        insights_custom_streams = list()

        for insight in insights:
            args = dict(
                api=default_args["api"],
                name=f"Custom{insight.name}",
                fields=list(set(insight.fields)),
                breakdowns=list(set(insight.breakdowns)),
                action_breakdowns=list(set(insight.action_breakdowns)),
                time_increment=insight.time_increment,
                start_date=insight.start_date or default_args["start_date"],
                end_date=insight.end_date or default_args["end_date"],
                insights_lookback_window=insight.insights_lookback_window or default_args["insights_lookback_window"],
            )
            insight_stream = AdsInsights(**args)
            insights_custom_streams.append(insight_stream)

        return streams + insights_custom_streams
