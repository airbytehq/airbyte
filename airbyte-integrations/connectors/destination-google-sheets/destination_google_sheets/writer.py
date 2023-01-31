import datetime
import json
from time import sleep

import gspread
import pandas as pd
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models.airbyte_protocol import (
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
)

logger = AirbyteLogger()


class GoogleSheetsDestinationWriter:
    """
    Data is written from this Destination to Google Sheets in this way:
        1. It create spreadsheets with name <source_name>_<stream_name> for every Stream came from Source.
        2. It just write every record to correspond Stream spreadsreet :)

    This Writer works this way:
        1. It __init__() with Google Sheets Client instance
        2. Destination instance calls queue_write_operation() with source_name, stream_name and record params.
            This method pass tuple ('<source_name>_<stream_name>', record) to write_buffer.
        3. If Destination got AirbyteMessage with type STATE (which by Airbyte specification means that next
            records bunch was passed) or length of write_buffer is more than flush_interval, flush() method
            calls.
        4. flush() method execute actual data write via Google Sheets client, then clean write_buffer.
        5. If delete_stream_entries() method calls, it clean all spreadsheet data correspond to stream. It happens
            when SyncMode for this Destination is set to overwrite.
    """

    write_buffer = {}
    flush_interval = 500

    def __init__(
        self,
        credentials: str,
        spreadsheet_url: str,
        configured_catalog: ConfiguredAirbyteCatalog,
    ):
        self.gs_client = gspread.service_account_from_dict(json.loads(credentials))
        self.spreadsheet = self.gs_client.open_by_url(spreadsheet_url)
        self.configured_catalog = configured_catalog

    def delete_stream_entries(self, stream_name: str):
        """Deletes all the records belonging to the input stream"""
        logger.info(f"Cleaning up {stream_name} worksheet")
        worksheet = self.get_stream_worksheet_if_exists_or_create(stream_name)
        try:
            self.spreadsheet.del_worksheet(worksheet)
        except:
            pass
        return self.get_stream_worksheet_if_exists_or_create(stream_name)

    def get_stream_related_worksheet_name(self, stream_name: str) -> str:
        return stream_name

    def get_worksheet_if_exists_or_create(self, worksheet_name: str):
        if self.is_worksheet_exists(worksheet_name):
            return self.spreadsheet.worksheet(worksheet_name)
        else:
            try:
                schema = self.get_json_schema_by_stream_name(
                    worksheet_name
                ).stream.json_schema
                return self.spreadsheet.add_worksheet(
                    worksheet_name, 1000, len(schema["properties"])
                )
            except:
                return self.spreadsheet.add_worksheet(worksheet_name, 1000, 60)

    def is_worksheet_exists(self, worksheet_name: str):
        return worksheet_name in list(
            map(lambda ws: ws.title, self.spreadsheet.worksheets())
        )

    def get_stream_worksheet_if_exists_or_create(self, stream_name: str):
        worksheet_name = self.get_stream_related_worksheet_name(stream_name)
        return self.get_worksheet_if_exists_or_create(worksheet_name)

    def queue_write_operation(self, record):
        stream_name = record.stream

        if not self.write_buffer.get(stream_name):
            self.write_buffer[stream_name] = []

        self.write_buffer[stream_name].append(record.data)

        if len(self.write_buffer[stream_name]) >= self.flush_interval:
            self.flush()

    def truncate_cell(self, value):
        try:
            if len(value) > 50000:
                logger.warn(f"value {value} truncated to 49999 length")
                return value[:49999]
            else:
                return value
        except:
            return value

    def apply_schema(self, df, configured_stream: ConfiguredAirbyteStream):
        types = {
            "integer": int,
            "string": str,
            "boolean": bool,
            "number": float,
            "array": list,
            "object": dict,
        }
        stream_properties = configured_stream.stream.json_schema["properties"]
        for property_name in stream_properties.keys():
            property = stream_properties[property_name]
            try:
                if isinstance(property["type"], list):
                    property_type = list(
                        filter(lambda type_name: type_name != "null", property["type"])
                    )[0]
                elif isinstance(property["type"], str):
                    property_type = property["type"]
                else:
                    continue

                if property_type in ["array", "object"]:
                    df[[property_name]] = df[[property_name]].applymap(
                        lambda value: json.dumps(value, ensure_ascii=False)
                    )
                else:
                    df[[property_name]] = df[[property_name]].astype(
                        types[property_type]
                    )

                def apply_datetime(value):
                    try:
                        formatted = datetime.datetime.strptime(
                            value, "%Y-%m-%dT%H:%M:%SZ"
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        return formatted
                    except Exception as e:
                        return value

                df[[property_name]] = df[[property_name]].applymap(apply_datetime)
            except Exception as e:
                logger.warn(f"Failed to cast field format. Exception: {e}")
                continue
        return df

    def get_json_schema_by_stream_name(self, stream_name: str):
        found = list(
            filter(
                lambda configured_stream: configured_stream.stream.name == stream_name,
                self.configured_catalog.streams,
            )
        )
        try:
            return found[0]
        except:
            return None

    def flush(self):
        for source_name in self.write_buffer.keys():
            ws = self.get_worksheet_if_exists_or_create(source_name)
            data = self.write_buffer[source_name]
            df = pd.DataFrame(data).fillna(value="")
            df = self.apply_schema(
                df, self.get_json_schema_by_stream_name(source_name)
            ).applymap(self.truncate_cell)

            write_header = False
            try:
                header_values = ws.row_values(1)
                if not header_values:
                    write_header = True
            except:
                write_header = True

            if write_header:
                logger.info(f"Writing header to {source_name} worksheet...")
                ws.append_row(
                    df.columns.values.tolist(),
                    table_range="A1",
                    value_input_option="USER_ENTERED",
                )

            list_of_values = df.values.tolist()
            if not list_of_values:
                continue
            logger.info(
                f"Writing {len(list_of_values)} records to {source_name} worksheet..."
            )

            ws.append_rows(
                list_of_values, table_range="A1", value_input_option="USER_ENTERED"
            )
            self.write_buffer[source_name].clear()
            sleep(2)
