#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json
import logging
from typing import Any, List, Mapping, Optional, Tuple, Type, Iterator

from airbyte_cdk.models import Type as MessageType
import facebook_business
import pendulum
from airbyte_cdk.models import (
    AdvancedAuth,
    AuthFlowType,
    AirbyteLogMessage,
    ConnectorSpecification,
    DestinationSyncMode,
    FailureType,
    OAuthConfigSpecification,
    SyncMode,
    Level,
    ConfiguredAirbyteStream,
    AirbyteMessage,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from source_facebook_marketing.api import API
from source_facebook_marketing.spec import ConnectorConfig
from source_facebook_marketing.streams import (
    Activities,
    AdAccount,
    AdCreatives,
    Ads,
    AdSets,
    AdsInsights,
    AdsInsightsActionCarouselCard,
    AdsInsightsActionConversionDevice,
    AdsInsightsActionProductID,
    AdsInsightsActionReaction,
    AdsInsightsActionType,
    AdsInsightsActionVideoSound,
    AdsInsightsActionVideoType,
    AdsInsightsAgeAndGender,
    AdsInsightsCountry,
    AdsInsightsDeliveryDevice,
    AdsInsightsDeliveryPlatform,
    AdsInsightsDeliveryPlatformAndDevicePlatform,
    AdsInsightsDemographicsAge,
    AdsInsightsDemographicsCountry,
    AdsInsightsDemographicsDMARegion,
    AdsInsightsDemographicsGender,
    AdsInsightsDma,
    AdsInsightsPlatformAndDevice,
    AdsInsightsRegion,
    Campaigns,
    CustomAudiences,
    CustomConversions,
    Images,
    Videos,
)

from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig, split_config

from .utils import validate_end_date, validate_start_date

logger = logging.getLogger("airbyte")
UNSUPPORTED_FIELDS = {"unique_conversions", "unique_ctr", "unique_clicks"}


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

    # Skip exceptions on missing streams
    raise_exception_on_missing_stream = False

    def _validate_and_transform(self, config: Mapping[str, Any]):
        config.setdefault("action_breakdowns_allow_empty", False)
        if config.get("end_date") == "":
            config.pop("end_date")

        config = ConnectorConfig.parse_obj(config)

        if config.start_date:
            config.start_date = pendulum.instance(config.start_date)

        if config.end_date:
            config.end_date = pendulum.instance(config.end_date)
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """Connection check to validate that the user-provided config can be used to connect to the underlying API

        :param logger: source logger
        :param config:  the user-input config object conforming to the connector's spec.json
        :return Tuple[bool, Any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        try:
            config = self._validate_and_transform(config)

            if config.end_date > pendulum.now():
                return False, "Date range can not be in the future."
            if config.start_date and config.end_date < config.start_date:
                return False, "End date must be equal or after start date."

            api = API(account_id=config.account_id, access_token=config.access_token, page_size=config.page_size,
                      google_service_account=config.google_service_account)

            logger.info(
                f"{len(api.accounts)} accounts selected: {sorted([int(account.get('account_id')) for account in api.accounts], reverse=True)}")

        except AirbyteTracedException as e:
            return False, f"{e.message}. Full error: {e.internal_message}"

        except Exception as e:
            return False, f"Unexpected error: {repr(e)}"

        # make sure that we have valid combination of "action_breakdowns" and "breakdowns" parameters
        for stream in self.get_custom_insights_streams(api, config):
            try:
                stream.check_breakdowns()
            except facebook_business.exceptions.FacebookRequestError as e:
                return False, e._api_error_message
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Type[Stream]]:
        """Discovery method, returns available streams

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        :return: list of the stream instances
        """
        config = self._validate_and_transform(config)
        if config.start_date:
            config.start_date = validate_start_date(config.start_date)
            config.end_date = validate_end_date(config.start_date, config.end_date)

        api = API(account_id=config.account_id, access_token=config.access_token, page_size=config.page_size,
                  google_service_account=config.google_service_account)

        # if start_date not specified then set default start_date for report streams to 2 years ago
        report_start_date = config.start_date or pendulum.now().add(years=-2)

        insights_args = dict(
            api=api,
            start_date=report_start_date,
            end_date=config.end_date,
            insights_lookback_window=config.insights_lookback_window
        )
        streams = [
            AdAccount(api=api),
            AdSets(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            Ads(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            AdCreatives(
                api=api,
                fetch_thumbnail_images=config.fetch_thumbnail_images,
                page_size=config.page_size,
            ),
            AdsInsights(page_size=config.page_size, **insights_args),
            AdsInsightsAgeAndGender(page_size=config.page_size, **insights_args),
            AdsInsightsCountry(page_size=config.page_size, **insights_args),
            AdsInsightsRegion(page_size=config.page_size, **insights_args),
            AdsInsightsDma(page_size=config.page_size, **insights_args),
            AdsInsightsPlatformAndDevice(page_size=config.page_size, **insights_args),
            AdsInsightsActionType(page_size=config.page_size, **insights_args),
            AdsInsightsActionCarouselCard(page_size=config.page_size, **insights_args),
            AdsInsightsActionConversionDevice(page_size=config.page_size, **insights_args),
            AdsInsightsActionProductID(page_size=config.page_size, **insights_args),
            AdsInsightsActionReaction(page_size=config.page_size, **insights_args),
            AdsInsightsActionVideoSound(page_size=config.page_size, **insights_args),
            AdsInsightsActionVideoType(page_size=config.page_size, **insights_args),
            AdsInsightsDeliveryDevice(page_size=config.page_size, **insights_args),
            AdsInsightsDeliveryPlatform(page_size=config.page_size, **insights_args),
            AdsInsightsDeliveryPlatformAndDevicePlatform(page_size=config.page_size, **insights_args),
            AdsInsightsDemographicsAge(page_size=config.page_size, **insights_args),
            AdsInsightsDemographicsCountry(page_size=config.page_size, **insights_args),
            AdsInsightsDemographicsDMARegion(page_size=config.page_size, **insights_args),
            AdsInsightsDemographicsGender(page_size=config.page_size, **insights_args),
            Campaigns(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            CustomConversions(
                api=api,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            CustomAudiences(
                api=api,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            Images(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            Videos(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
            Activities(
                api=api,
                start_date=config.start_date,
                end_date=config.end_date,
                include_deleted=config.include_deleted,
                page_size=config.page_size,
            ),
        ]

        return streams + self.get_custom_insights_streams(api, config)

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
            advanced_auth=AdvancedAuth(
                auth_flow_type=AuthFlowType.oauth2_0,
                oauth_config_specification=OAuthConfigSpecification(
                    complete_oauth_output_specification={
                        "type": "object",
                        "properties": {
                            "access_token": {
                                "type": "string",
                                "path_in_connector_config": ["access_token"],
                            }
                        },
                    },
                    complete_oauth_server_input_specification={
                        "type": "object",
                        "properties": {"client_id": {"type": "string"}, "client_secret": {"type": "string"}},
                    },
                    complete_oauth_server_output_specification={
                        "type": "object",
                        "additionalProperties": True,
                        "properties": {
                            "client_id": {"type": "string", "path_in_connector_config": ["client_id"]},
                            "client_secret": {"type": "string", "path_in_connector_config": ["client_secret"]},
                        },
                    },
                ),
            ),
        )

    def get_custom_insights_streams(self, api: API, config: ConnectorConfig) -> List[Type[Stream]]:
        """return custom insights streams"""
        streams = []
        for insight in config.custom_insights or []:
            insight_fields = set(insight.fields)
            if insight_fields.intersection(UNSUPPORTED_FIELDS):
                # https://github.com/airbytehq/oncall/issues/1137
                message = (
                    f"The custom fields `{insight_fields.intersection(UNSUPPORTED_FIELDS)}` are not a valid configuration for"
                    f" `{insight.name}'. Review Facebook Marketing's docs https://developers.facebook.com/docs/marketing-api/reference/ads-action-stats/ for valid breakdowns."
                )
                raise AirbyteTracedException(
                    message=message,
                    failure_type=FailureType.config_error,
                )
            stream = AdsInsights(
                api=api,
                name=f"Custom{insight.name}",
                fields=list(insight_fields),
                breakdowns=list(set(insight.breakdowns)),
                action_breakdowns=list(set(insight.action_breakdowns)),
                action_breakdowns_allow_empty=config.action_breakdowns_allow_empty,
                action_report_time=insight.action_report_time,
                time_increment=insight.time_increment,
                start_date=insight.start_date or config.start_date or pendulum.now().add(years=-2),
                end_date=insight.end_date or config.end_date,
                insights_lookback_window=insight.insights_lookback_window or config.insights_lookback_window,
                level=insight.level,
            )
            streams.append(stream)
        return streams
