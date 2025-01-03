#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
import logging
import socket
from typing import Any, Generator, List, Mapping, MutableMapping, Optional, Union

from apiclient import errors
from google.auth import exceptions as google_exceptions
from requests.status_codes import codes as status_codes

from airbyte_cdk.models import FailureType
from airbyte_cdk.models.airbyte_protocol import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteStateMessage,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.source import Source
from airbyte_cdk.sources.streams.checkpoint import FullRefreshCheckpointReader
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import as_airbyte_message

from .client import GoogleSheetsClient
from .helpers import Helpers
from .models.spreadsheet import Spreadsheet
from .models.spreadsheet_values import SpreadsheetValues
from .utils import exception_description_by_status_code, safe_name_conversion


# override default socket timeout to be 10 mins instead of 60 sec.
# on behalf of https://github.com/airbytehq/oncall/issues/242
DEFAULT_SOCKET_TIMEOUT: int = 600
socket.setdefaulttimeout(DEFAULT_SOCKET_TIMEOUT)


class SourceGoogleSheets(Source):
    """
    Spreadsheets API Reference: https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
    """

    def check(self, logger: logging.Logger, config: json) -> AirbyteConnectionStatus:
        # Check involves verifying that the specified spreadsheet is reachable with our credentials.
        try:
            client = GoogleSheetsClient(self.get_credentials(config))
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Please use valid credentials json file. Error: {e}")

        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])

        try:
            spreadsheet = client.get(spreadsheetId=spreadsheet_id, includeGridData=False)
        except errors.HttpError as err:
            message = "Config error: "
            # Give a clearer message if it's a common error like 404.
            if err.resp.status == status_codes.NOT_FOUND:
                message += "The spreadsheet link is not valid. Enter the URL of the Google spreadsheet you want to sync."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            ) from err
        except google_exceptions.GoogleAuthError as err:
            message = "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            ) from err

        # Check for duplicate headers
        spreadsheet_metadata = Spreadsheet.parse_obj(spreadsheet)
        grid_sheets = Helpers.get_grid_sheets(spreadsheet_metadata)

        duplicate_headers_in_sheet = {}
        for sheet_name in grid_sheets:
            try:
                header_row_data = Helpers.get_first_row(client, spreadsheet_id, sheet_name)
                if config.get("names_conversion"):
                    header_row_data = [safe_name_conversion(h) for h in header_row_data]
                _, duplicate_headers = Helpers.get_valid_headers_and_duplicates(header_row_data)
                if duplicate_headers:
                    duplicate_headers_in_sheet[sheet_name] = duplicate_headers
            except Exception as err:
                if str(err).startswith("Expected data for exactly one row for sheet"):
                    logger.warn(f"Skip empty sheet: {sheet_name}")
                else:
                    logger.error(str(err))
                    return AirbyteConnectionStatus(
                        status=Status.FAILED, message=f"Unable to read the schema of sheet {sheet_name}. Error: {str(err)}"
                    )
        if duplicate_headers_in_sheet:
            duplicate_headers_error_message = ", ".join(
                [
                    f"[sheet:{sheet_name}, headers:{duplicate_sheet_headers}]"
                    for sheet_name, duplicate_sheet_headers in duplicate_headers_in_sheet.items()
                ]
            )
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="The following duplicate headers were found in the following sheets. Please fix them to continue: "
                + duplicate_headers_error_message,
            )

        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(self, logger: logging.Logger, config: json) -> AirbyteCatalog:
        client = GoogleSheetsClient(self.get_credentials(config))
        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])
        try:
            logger.info(f"Running discovery on sheet {spreadsheet_id}")
            spreadsheet_metadata = Spreadsheet.parse_obj(client.get(spreadsheetId=spreadsheet_id, includeGridData=False))
            grid_sheets = Helpers.get_grid_sheets(spreadsheet_metadata)
            streams = []
            for sheet_name in grid_sheets:
                try:
                    header_row_data = Helpers.get_first_row(client, spreadsheet_id, sheet_name)
                    if config.get("names_conversion"):
                        header_row_data = [safe_name_conversion(h) for h in header_row_data]
                    stream = Helpers.headers_to_airbyte_stream(logger, sheet_name, header_row_data)
                    streams.append(stream)
                except Exception as err:
                    if str(err).startswith("Expected data for exactly one row for sheet"):
                        logger.warn(f"Skip empty sheet: {sheet_name}")
                    else:
                        logger.error(str(err))
            return AirbyteCatalog(streams=streams)

        except errors.HttpError as err:
            error_description = exception_description_by_status_code(err.resp.status, spreadsheet_id)
            config_error_status_codes = [status_codes.NOT_FOUND, status_codes.FORBIDDEN]
            if err.resp.status in config_error_status_codes:
                message = f"{error_description}. {err.reason}."
                raise AirbyteTracedException(
                    message=message,
                    internal_message=message,
                    failure_type=FailureType.config_error,
                ) from err
            raise Exception(f"Could not discover the schema of your spreadsheet. {error_description}. {err.reason}.")
        except google_exceptions.GoogleAuthError as err:
            message = "Access to the spreadsheet expired or was revoked. Re-authenticate to restore access."
            raise AirbyteTracedException(
                message=message,
                internal_message=message,
                failure_type=FailureType.config_error,
            ) from err

    def _read(
        self,
        logger: logging.Logger,
        config: json,
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Generator[AirbyteMessage, None, None]:
        client = GoogleSheetsClient(self.get_credentials(config))
        client.Backoff.row_batch_size = config.get("batch_size", 200)

        sheet_to_column_name = Helpers.parse_sheet_and_column_names_from_catalog(catalog)
        stream_instances = {s.stream.name: s.stream for s in catalog.streams}
        state_manager = ConnectorStateManager(stream_instance_map=stream_instances, state=state or {})
        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])

        logger.info(f"Starting syncing spreadsheet {spreadsheet_id}")
        # For each sheet in the spreadsheet, get a batch of rows, and as long as there hasn't been
        # a blank row, emit the row batch
        sheet_to_column_index_to_name = Helpers.get_available_sheets_to_column_index_to_name(
            client, spreadsheet_id, sheet_to_column_name, config.get("names_conversion")
        )
        sheet_row_counts = Helpers.get_sheet_row_count(client, spreadsheet_id)
        logger.info(f"Row counts: {sheet_row_counts}")
        for sheet in sheet_to_column_index_to_name.keys():
            logger.info(f"Syncing sheet {sheet}")
            stream = stream_instances.get(sheet)
            yield as_airbyte_message(stream, AirbyteStreamStatus.STARTED)
            checkpoint_reader = FullRefreshCheckpointReader([])
            _ = checkpoint_reader.next()
            # We revalidate the sheet here to avoid errors in case the sheet was changed after the sync started
            is_valid, reason = Helpers.check_sheet_is_valid(client, spreadsheet_id, sheet)
            if not is_valid:
                logger.info(f"Skipping syncing sheet {sheet}: {reason}")
                yield self._checkpoint_state(checkpoint_reader.get_checkpoint(), state_manager, sheet, None)
                yield as_airbyte_message(stream, AirbyteStreamStatus.INCOMPLETE)
                continue

            column_index_to_name = sheet_to_column_index_to_name[sheet]
            row_cursor = 2  # we start syncing past the header row
            # For the loop, it is necessary that the initial row exists when we send a request to the API,
            # if the last row of the interval goes outside the sheet - this is normal, we will return
            # only the real data of the sheet and in the next iteration we will loop out.
            while row_cursor <= sheet_row_counts[sheet]:
                row_batch = SpreadsheetValues.parse_obj(
                    client.get_values(
                        sheet=sheet,
                        row_cursor=row_cursor,
                        spreadsheetId=spreadsheet_id,
                        majorDimension="ROWS",
                    )
                )

                row_cursor += client.Backoff.row_batch_size + 1
                # there should always be one range since we requested only one
                value_ranges = row_batch.valueRanges[0]

                if not value_ranges.values:
                    break

                row_values = value_ranges.values
                if len(row_values) == 0:
                    break

                yield as_airbyte_message(stream, AirbyteStreamStatus.RUNNING)
                for row in row_values:
                    if not Helpers.is_row_empty(row) and Helpers.row_contains_relevant_data(row, column_index_to_name.keys()):
                        yield AirbyteMessage(type=Type.RECORD, record=Helpers.row_data_to_record_message(sheet, row, column_index_to_name))

            yield self._checkpoint_state(checkpoint_reader.get_checkpoint(), state_manager, sheet, None)
            yield as_airbyte_message(stream, AirbyteStreamStatus.COMPLETE)

    def _checkpoint_state(
        self,
        stream_state: Mapping[str, Any],
        state_manager,
        stream_name: str,
        stream_namespace: Optional[str],
    ) -> AirbyteMessage:
        state_manager.update_state_for_stream(stream_name, stream_namespace, stream_state)
        return state_manager.create_state_message(stream_name, stream_namespace)

    def read(
        self,
        logger: logging.Logger,
        config: json,
        catalog: ConfiguredAirbyteCatalog,
        state: Union[List[AirbyteStateMessage], MutableMapping[str, Any]] = None,
    ) -> Generator[AirbyteMessage, None, None]:
        spreadsheet_id = Helpers.get_spreadsheet_id(config["spreadsheet_id"])
        try:
            yield from self._read(logger, config, catalog, state)
        except errors.HttpError as e:
            error_description = exception_description_by_status_code(e.status_code, spreadsheet_id)

            if e.status_code == status_codes.FORBIDDEN:
                raise AirbyteTracedException(
                    message=f"Stopped syncing process. {error_description}",
                    internal_message=error_description,
                    failure_type=FailureType.config_error,
                ) from e
            if e.status_code == status_codes.TOO_MANY_REQUESTS:
                raise AirbyteTracedException(
                    message=f"Stopped syncing process due to rate limits. {error_description}",
                    internal_message=error_description,
                    failure_type=FailureType.transient_error,
                ) from e
            else:
                logger.info(f"{e.status_code}: {e.reason}. {error_description}")
                raise AirbyteTracedException(
                    message=f"Stopped syncing process. {error_description}",
                    internal_message=error_description,
                    failure_type=FailureType.transient_error,
                ) from e
        finally:
            logger.info(f"Finished syncing spreadsheet {spreadsheet_id}")

    @staticmethod
    def get_credentials(config):
        # backward compatible with old style config
        if config.get("credentials_json"):
            credentials = {"auth_type": "Service", "service_account_info": config.get("credentials_json")}
            return credentials

        return config.get("credentials")
