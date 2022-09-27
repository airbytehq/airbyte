#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import csv
import io
import json
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .fields import API_REPORT_BUILDER_MAPPING, sanitize

# Mapping between the schema names and the report types in the report builder
REPORT_TYPE_MAPPING = {
    "audience_composition": "TYPE_AUDIENCE_COMPOSITION",
    "reach": "TYPE_REACH_AND_FREQUENCY",
    "floodlight": "FLOODLIGHT",
    "standard": "TYPE_GENERAL",
    "unique_reach_audience": "TYPE_REACH_AUDIENCE",
}


def chunk_date_range(
    start_date: str,
    field: str,
    end_date: str = None,
    range_days: int = None,
) -> Iterable[Mapping[str, any]]:
    """
    Passing optional parameter end_date for testing
    Returns a list of the beginning and ending timestamps of each `range_days` between the start date and now.
    The return value is a list of dicts {'date': str} which can be used directly with the Slack API
    """
    intervals = []
    end_date = pendulum.parse(end_date) if end_date else pendulum.yesterday()
    start_date = pendulum.parse(start_date)

    # to return some state when state is abnormal
    if start_date > end_date:
        start_date = end_date

    while start_date < end_date:
        intervals.append(
            {
                "start_date": start_date.to_date_string(),
                "end_date": end_date.to_date_string(),
            }
        )
        start_date = start_date.add(days=range_days)
    return intervals


class DBM:
    QUERY_TEMPLATE_PATH = "source_dv_360/queries/query_template.json"  # Template for creating the query object
    DBM_SCOPE = "doubleclickbidmanager"  # Scope required to fetch data

    def __init__(self, credentials: Credentials, partner_id: str, scope: str = DBM_SCOPE, version: str = "v1.1"):
        self.service = build(scope, version, credentials=credentials)  # build a service with scope dbm
        self.partner_id = partner_id

    @staticmethod
    def get_date_params_ms(start_date: str, end_date: str = None) -> Tuple[str, str]:
        """
        Returns `start_date` and `end_date` in milliseconds
        """
        start_date = pendulum.parse(start_date)
        # if end_date is null, take date until yesterday
        end_date = pendulum.parse(end_date) if end_date else pendulum.yesterday()

        # check if start date is after end date
        if start_date > end_date:
            start_date = end_date

        start_date_ms = str(int(start_date.timestamp() * 1000))
        end_date_ms = str(int(end_date.timestamp() * 1000))

        return start_date_ms, end_date_ms

    @staticmethod
    def get_fields_from_schema(schema: Mapping[str, Any], catalog_fields: List[str]) -> List[str]:
        """
        Get list of fields in a given schema
        :param schema: the list of fields to be converted
        :param catalog_fields: the list of fields to be converted

        :return: A list of fields
        """
        schema_fields = schema.get("properties").keys()
        fields = [field for field in schema_fields if field in catalog_fields]
        return fields

    @staticmethod
    def convert_fields(fields: List[str]) -> List[str]:
        """
        Convert a list of fields into the API naming
        :param fields: the list of fields to be converted

        :return: A list of converted fields
        """
        return [API_REPORT_BUILDER_MAPPING[key] for key in fields]

    @staticmethod
    def get_dimensions_from_fields(fields: List[str]) -> List[str]:
        """
        Get a list of dimensions from a list of fields. Dimensions start with FILTER_
        :param fields: A list of fields from the stream

        :return: A list of dimensions in the naming form of the API
        """
        conv_fields = DBM.convert_fields(fields)
        dimensions = [field for field in conv_fields if field.startswith("FILTER")]
        return dimensions

    @staticmethod
    def get_metrics_from_fields(fields: List[str]) -> List[str]:
        """
        Get a list of metrics from from a list of fields. Metrics start with METRIC_
        :param fields: A list of fields from the stream

        :return: A list of metrics in the naming form of the API
        """
        conv_fields = DBM.convert_fields(fields)
        metrics = [field for field in conv_fields if field.startswith("METRIC")]
        return metrics

    @staticmethod
    def set_partner_filter(query: Mapping[str, Any], partner_id: str):
        """
        set the partner id filter to the partner id in the config
        :param query: the query object where the filter is to be set
        """
        filters = query.get("params").get("filters")
        if filters:
            partner_filter_index = next(
                (index for (index, filter) in enumerate(filters) if filter["type"] == "FILTER_PARTNER"), None
            )  # get the index of the partner filter
            if partner_filter_index is not None:
                query["params"]["filters"][partner_filter_index]["value"] = partner_id  # set filter to the partner id in the config

    @staticmethod
    def create_query_object(
        report_name: str,
        dimensions: List[str],
        metrics: List[str],
        partner_id: str,
        start_date: str,
        end_date: str,
        filters: List[dict] = [],
    ) -> Mapping[str, Any]:
        """
        Create a query object using the query template and a list of parameter for the query
        :param report_name: Name of the report
        :param dimensions: List of dimensions
        :param metrics: list of metrics
        :param start_date: Start date of the report, in the same form of the date in the config, as specified in the spec
        :param end_date: End date of the report, in the same form of the date in the config, as specified in the spec
        :param filters: additional filters to be set

        :return the query object created according to the template
        """
        with open(DBM.QUERY_TEMPLATE_PATH, "r") as template:
            query_body = json.loads(template.read())

        # get dates in ms
        start_date_ms, end_date_ms = DBM.get_date_params_ms(start_date, end_date)

        DBM.set_partner_filter(query_body, partner_id)  # Set partner Id in the filter
        query_body["metadata"]["title"] = report_name
        query_body["params"]["type"] = REPORT_TYPE_MAPPING[report_name]  # get the report type from the mapping
        query_body["params"]["groupBys"] = dimensions  # dimensions are put in the groupBy section of the query
        query_body["params"]["filters"].extend(filters)  # Add additional filters if needed
        query_body["params"]["metrics"] = metrics
        query_body["reportDataStartTimeMs"] = start_date_ms
        query_body["reportDataEndTimeMs"] = end_date_ms
        return query_body

    def convert_schema_into_query(
        self,
        schema: Mapping[str, Any],
        report_name: str,
        catalog_fields: List[str],
        partner_id: str,
        filters: List[dict],
        start_date: str,
        end_date: str,
    ) -> str:
        """
        Create and run a query from the given schema
        :param report_name: Name of the report
        :param catalog_fields: List of fields which names are sanitized
        :param start_date: Start date of the report, in the same form of the date in the config, as specified in the spec
        :param end_date: End date of the report, in the same form of the date in the config, as specified in the spec
        :param filters: additional filters to be set

        :return the query object created according to the template
        """
        fields = self.get_fields_from_schema(schema, catalog_fields)
        query = self.create_query_object(
            report_name=report_name,
            dimensions=self.get_dimensions_from_fields(fields),
            metrics=self.get_metrics_from_fields(fields),
            start_date=start_date,
            end_date=end_date,
            partner_id=partner_id,
            filters=filters or [],
        )
        create_query = self.service.queries().createquery(body=query).execute()  # Create query
        get_query = (
            self.service.queries().getquery(queryId=create_query.get("queryId")).execute()
        )  # get the query which will include the report url
        return get_query


class DBMStream(Stream, ABC):
    """
    Base stream class
    """

    primary_key = None

    def __init__(self, credentials: Credentials, partner_id: str, filters: List[dict], start_date: str, end_date: str = None):
        self.dbm = DBM(credentials=credentials, partner_id=partner_id)
        self._start_date = start_date
        self._end_date = end_date
        self._partner_id = partner_id
        self._filters = filters

    def get_query(self, catalog_fields: List[str], stream_slice: Mapping[str, Any]) -> Iterable[Mapping]:
        """
        Create and run a query from the datastream schema and parameters, and a list of fields provided in the configured catalog
        :param catalog_fields: A list of fields provided in the configured catalog

        :return the created query
        """
        query = self.dbm.convert_schema_into_query(
            schema=self.get_json_schema(),
            catalog_fields=catalog_fields,
            filters=self._filters,
            report_name=self.name,
            start_date=self._start_date,
            end_date=self._end_date,
            partner_id=self._partner_id,
        )
        return query

    def read_records(self, catalog_fields: List[str], stream_slice: Mapping[str, Any] = None, sync_mode=None):
        """
        Get the report from the url specified in the created query. The report is in csv form, with
        additional meta data below the data that need to be remove.
        :param catalog_fields: A list of fields provided in the configured catalog to create the query

        :return a generator of dict rows from the file
        """
        query = self.get_query(catalog_fields=catalog_fields, stream_slice=stream_slice)  # create and run the query
        report_url = query["metadata"]["googleCloudStoragePathForLatestReport"]  # Take the url of the generated report
        with io.StringIO(requests.get(report_url).text) as csv_response:
            header = csv_response.readline().split(",")  # get the header of the file
            header = [sanitize(field) for field in header]  # sanitize the field names
            data = self.buffer_reader(csv_response)  # Remove the unnecessary rows that do not have data
            reader = csv.DictReader(data, fieldnames=header)  # convert csv data into dict rows to be yielded by the generator
            report_type = query["params"]["type"]
            list_reader = list(reader)
            nb_rows = len(list_reader)
            for index, row in enumerate(list_reader):
                # In the case of the standard report, we are getting an additional summary row, therefore we need to exclude it.
                if not (report_type == "TYPE_GENERAL" and index > nb_rows - 2):
                    yield row

    def buffer_reader(self, buffer: io.StringIO):
        """
        Yield all lines from a file text buffer until the empty line is reached

        :return a generator of dict rows from the file
        """
        for line in buffer.readlines():
            if line != "\n":  # NB: the last non empty line contains the sum of the metrics in the data
                yield line
            else:
                break


class DBMIncrementalStream(DBMStream, ABC):
    cursor_field = "date"
    primary_key = None
    range_days = 30  # range of stream slice

    def __init__(self, credentials: Credentials, partner_id: str, filters: List[dict], start_date: str, end_date: str = None):
        super().__init__(credentials, partner_id, filters, start_date, end_date)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Update stream state from latest record
        """
        current_stream_state = current_stream_state or {}
        record_value = latest_record[self.cursor_field]
        state_value = current_stream_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))
        toreturn = {
            self.cursor_field: max_cursor.to_date_string(),
        }
        return toreturn

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Slice the stream by date periods.
        """
        stream_state = stream_state or {}
        start_date = stream_state.get(self.cursor_field) or self._start_date
        date_chunks = chunk_date_range(
            start_date=start_date,
            end_date=self._end_date,
            field=self.cursor_field,
            range_days=self.range_days,
        )
        for chunk in date_chunks:
            yield chunk

    def read_records(
        self,
        sync_mode: SyncMode,
        catalog_fields: List[str],
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method is overridden to update `start_date` key in the `stream_slice` with the latest read record's cursor value.
        """
        records = super().read_records(catalog_fields=catalog_fields, sync_mode=sync_mode, stream_slice=stream_slice)
        for record in records:
            self.state = self.get_updated_state(self.state, record)
            yield record

    def get_query(self, catalog_fields: List[str], stream_slice: Mapping[str, Any]) -> Iterable[Mapping]:
        """
        Create and run a query from the datastream schema and parameters, and a list of fields provided in the configured catalog
        :param catalog_fields: A list of fields provided in the configured catalog

        :return the created query
        """
        query = self.dbm.convert_schema_into_query(
            schema=self.get_json_schema(),
            catalog_fields=catalog_fields,
            filters=self._filters,
            report_name=self.name,
            start_date=stream_slice.get("start_date"),
            end_date=stream_slice.get("end_date"),
            partner_id=self._partner_id,
        )
        return query


class AudienceComposition(DBMIncrementalStream):
    """
    Audience Composition stream
    """

    primary_key = None


class Floodlight(DBMIncrementalStream):
    """
    Floodlight stream
    """

    primary_key = None


class Standard(DBMIncrementalStream):
    """
    Standard stream
    """

    primary_key = None


class UniqueReachAudience(DBMIncrementalStream):
    """
    Unique Reach Audience stream
    """

    primary_key = None


class Reach(DBMIncrementalStream):
    """
    Reach stream
    """

    primary_key = None
