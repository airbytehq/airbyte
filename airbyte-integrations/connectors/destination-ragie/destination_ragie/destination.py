# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import logging
from typing import Any, Iterable, Mapping

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    Status,
    Type,
)
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType

from .client import RagieClient
from .config import RagieConfig
from .writer import RagieWriter


# Configure logging for CDK usage
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger("airbyte.destination_ragie")


class DestinationRagie(Destination):
    """
    Airbyte Destination Connector for Ragie.ai.
    """

    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        """
        Reads message stream, configures Ragie client and writer, handles sync modes,
        and yields state messages.
        """
        try:
            config_model = RagieConfig.model_validate(config)
            client = RagieClient(config=config_model)
            writer = RagieWriter(client=client, config=config_model, catalog=configured_catalog)
        except Exception as e:
            logger.error(f"Failed to initialize connector: {e}", exc_info=True)
            # Yield a state message? Or just raise? Raising is better to signal init failure.
            raise AirbyteTracedException(
                message="Failed to initialize the Ragie destination connector. Please check configuration.",
                internal_message=str(e),
                failure_type=FailureType.config_error,
            ) from e

        logger.info("Starting Ragie destination write operation.")

        try:
            # --- Handle Overwrite Mode ---
            # Delete existing data for streams marked as Overwrite *before* processing records
            writer.delete_streams_to_overwrite()

            # --- Process Messages ---
            processed_records = 0
            for message in input_messages:
                if message.type == Type.STATE:
                    # On STATE message: Flush buffer, then yield state
                    logger.info(f"Received STATE message: {message.state.data}. Yielding state.")
                    try:
                        yield message
                    except Exception as e:
                        logger.error(f"Exception during Yielding on STATE message: {e}", exc_info=True)
                        # Re-raise to signal failure to Airbyte platform
                        raise e

                elif message.type == Type.RECORD:
                    try:
                        writer.queue_write_operation(message.record)
                        processed_records += 1
                        if processed_records % 10 == 0:  # Log progress periodically
                            logger.info(f"Processed {processed_records} records...")
                    except Exception as e:
                        # Error processing a single record - log and potentially continue or fail?
                        # Let's fail fast if queue_write_operation raises something critical.
                        logger.error(f"Error processing Airbyte Record: {e}", exc_info=True)
                        raise e  # Re-raise to signal failure

                else:
                    # Ignore other message types (LOG, TRACE, etc.)
                    logger.debug(f"Ignoring message of type: {message.type}")

            logger.info(f"Write operation completed. Total records processed: {processed_records}")

        except Exception as e:
            # Catch-all for errors during the write loop or final flush
            logger.critical(f"Critical error during Ragie write operation: {e}", exc_info=True)
            # Don't yield any state if a critical error occurred after the last successful state commit.
            # Airbyte platform will handle the failure based on the raised exception.
            # Ensure the original exception is raised if it's already an AirbyteTracedException
            if isinstance(e, AirbyteTracedException):
                raise e
            else:
                raise AirbyteTracedException(
                    message="An error occurred during data writing to Ragie.",
                    internal_message=str(e),
                    failure_type=FailureType.system_error,  # Or determine failure type if possible
                ) from e

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests connectivity and authentication with Ragie API using the provided config.
        """
        logger.info("Checking connection to Ragie...")
        try:
            config_model = RagieConfig.model_validate(config)
            client = RagieClient(config=config_model)
            error_message = client.check_connection()

            if error_message:
                logger.error(f"Connection check failed: {error_message}")
                return AirbyteConnectionStatus(status=Status.FAILED, message=error_message)
            else:
                logger.info("Connection check successful.")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except ValueError as e:  # Handles Pydantic validation errors
            logger.error(f"Configuration validation error: {e}")
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Configuration validation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during connection check: {e}", exc_info=True)
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An unexpected error occurred during connection check: {repr(e)}")

    def spec(self, *args: Any, **kwargs: Any) -> ConnectorSpecification:
        """
        Returns the connector specification (schema defining configuration).
        """
        return ConnectorSpecification(
            documentationUrl="https://github.com/YourRepo/airbyte-destination-ragie",  # TODO: Update URL
            supportsIncremental=True,  # Because we handle state messages
            supported_destination_sync_modes=[
                DestinationSyncMode.overwrite,
                DestinationSyncMode.append,
                DestinationSyncMode.append_dedup,  # Support all modes
            ],
            connectionSpecification=RagieConfig.model_json_schema(),
        )
