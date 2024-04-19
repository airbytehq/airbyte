#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import base64
import logging
from abc import ABC
from typing import Any, Dict, Iterable, List, Mapping, NamedTuple, Optional, Tuple, Union, cast

import requests
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests.exceptions import HTTPError

from .exception import AvailableFieldsAccessDeniedError
from .utils import chunk_iterable


class BambooHrStream(HttpStream, ABC):
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = config
        super().__init__(authenticator=config["authenticator"])

    @property
    def url_base(self) -> str:
        return f"https://api.bamboohr.com/api/gateway.php/{self.config['subdomain']}/v1/"

    def request_headers(  # type: ignore
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        BambooHR does not support pagination.
        """
        pass


class MetaTablesStream(BambooHrStream):
    primary_key = None  # type: ignore

    def path(self, **kwargs) -> str:  # type: ignore
        return "meta/tables"

    def parse_response(
        self,
        response: requests.Response,
        **kwarg,  # type: ignore
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json()


class BambooMetaField(NamedTuple):
    """Immutable typed representation of what is returned from the meta/fields
    endpoint."""

    id: Union[int, str]
    name: str
    type: str
    alias: Optional[str] = None
    deprecated: Optional[bool] = None


class MetaFieldsStream(BambooHrStream):
    primary_key = None  # type: ignore

    def path(self, **kwargs) -> str:  # type: ignore
        return "meta/fields"

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,  # type: ignore
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json()


class BambooMetaTableField(NamedTuple):
    """Immutable typed representation of the field data returned from the meta/tables
    endpoint."""

    id: int
    name: str
    alias: str
    type: str


class BambooMetaTable(NamedTuple):
    """Immutable typed representation of what is returned from the meta/tables
    endpoint."""

    alias: str
    fields: List[BambooMetaTableField]


class TablesStream(BambooHrStream):
    primary_key = None  # type: ignore
    raise_on_http_errors = False  # type: ignore
    skip_http_status_codes = [
        requests.codes.NOT_FOUND,
        requests.codes.INTERNAL_SERVER_ERROR,
    ]

    @staticmethod
    def convert_raw_meta_table_to_typed(raw_meta_table: Mapping[str, Any]) -> BambooMetaTable:
        """
        Converts a raw meta table to a typed BambooMetaTable.
        """
        return BambooMetaTable(
            alias=raw_meta_table.get("alias", ""),
            fields=[BambooMetaTableField(**field) for field in raw_meta_table.get("fields", [])],
        )

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code in self.skip_http_status_codes:
            return False
        else:
            return super().should_retry(response)

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        if stream_slice is not None:
            table_name = stream_slice["table"]
            for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
                # If the record is empty, skip it.
                # This may occur if parse_response yields an empty record,
                # which can happen if the response is not 2xx.
                if record == {} or not isinstance(record, Mapping):
                    self.logger.warn(f"Empty record or non-map record encountered in TablesStream. Record: {record}")
                else:
                    # Augment the record for easier lookup/better
                    # performance in the destination.
                    new_record: Mapping[str, Any] = {
                        "id": record["id"],
                        "employee_id": record["employeeId"],
                        "table_name": table_name,
                        "data": record,
                    }
                    yield new_record
        else:
            self.logger.error("Stream slice is None in TablesStream.")
            yield {}

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:  # type: ignore
        # Each table has an 'alias' field that we use to grab
        # all values.  See `path` method for how it's used in the URL.
        available_tables: List[BambooMetaTable] = self.config.get("available_tables", [])
        for meta_table in available_tables:  # Add default value of empty list
            table = meta_table.alias
            yield {"table": table}

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:  # type: ignore
        target_table = stream_slice["table"]
        return f"employees/all/tables/{target_table}"

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        **kwargs,  # type: ignore
    ) -> Iterable[Mapping[str, Any]]:
        try:
            # This will raise an exception if the response is not 2xx
            response.raise_for_status()
            yield from response.json()
        except HTTPError as e:
            # Check to see if this error code is one we expect.
            # If so, raise an error.
            if not (self.skip_http_status_codes and e.response.status_code in self.skip_http_status_codes):
                raise e

            # Otherwise, just log a warning.
            self.logger.warning(f"Stream `{self.name}`. An error occurred, details: {e}. Skipping for now.")
            yield {}


class CustomReportsStream(BambooHrStream):
    primary_key = None  # type: ignore

    def __init__(self, *args, **kwargs):  # type: ignore
        super().__init__(*args, **kwargs)  # type: ignore

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:  # type: ignore
        available_fields: List[str] = self.config.get("available_fields", [])
        for fields in chunk_iterable(available_fields, 100):
            yield {"fields": fields}

    def path(self, **kwargs) -> str:  # type: ignore
        return "reports/custom"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        stream_state: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            # Augment the record with the table name.
            if record == {} or not isinstance(record, Mapping):
                self.logger.warn("Empty record or non-map record encountered in CustomReportsStream.")
            else:
                new_record = {
                    "id": record["id"],
                    "data": record,
                }
                yield new_record

    @property
    def http_method(self) -> str:
        return "POST"

    @staticmethod
    def get_default_bamboo_fields() -> List[str]:
        # As per https://documentation.bamboohr.com/docs/list-of-field-names
        return [
            "acaStatusCategory",
            "address1",
            "address2",
            "age",
            "bestEmail",
            "birthday",
            "bonusAmount",
            "bonusComment",
            "bonusDate",
            "bonusReason",
            "city",
            "commissionAmount",
            "commissionComment",
            "commissionDate",
            "commisionDate",
            "country",
            "createdByUserId",
            "dateOfBirth",
            "department",
            "division",
            "eeo",
            "employeeNumber",
            "employmentHistoryStatus",
            "ethnicity",
            "exempt",
            "firstName",
            "flsaCode",
            "fullName1",
            "fullName2",
            "fullName3",
            "fullName4",
            "fullName5",
            "displayName",
            "gender",
            "hireDate",
            "originalHireDate",
            "homeEmail",
            "homePhone",
            "id",
            "isPhotoUploaded",
            "jobTitle",
            "lastChanged",
            "lastName",
            "location",
            "maritalStatus",
            "middleName",
            "mobilePhone",
            "nationalId",
            "nationality",
            "nin",
            "payChangeReason",
            "payGroup",
            "payGroupId",
            "payRate",
            "payRateEffectiveDate",
            "payType",
            "paidPer",
            "paySchedule",
            "payScheduleId",
            "payFrequency",
            "includeInPayroll",
            "timeTrackingEnabled",
            "preferredName",
            # "ssn",  # This is supported, but we don't want it.
            "sin",
            "standardHoursPerWeek",
            "state",
            "stateCode",
            "status",
            "supervisor",
            "supervisorId",
            "supervisorEId",
            "supervisorEmail",
            "terminationDate",
            "workEmail",
            "workPhone",
            "workPhonePlusExtension",
            "workPhoneExtension",
            "zipcode",
        ]

    @staticmethod
    def convert_field_to_id(field: BambooMetaField) -> str:
        """Converts a BambooMetaField to an id for the custom report endpoint."""

        # The reports/custom endpoint takes a list of fields, each of
        # which can be referred to by its alias (if one exists) or
        # by its stringified id.
        if field.alias is None:
            return str(id)
        else:
            return field.alias

    def request_body_json(  # type: ignore
        self,
        stream_slice: Mapping[str, Any] | None = None,
        **kwargs,  # type: ignore
    ) -> Optional[Mapping[str, Any]]:
        fields: List[str] = stream_slice["fields"] if stream_slice is not None else []
        return {"title": "Airbyte", "fields": fields}

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,  # type: ignore
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json()["employees"]


class EmployeesDirectoryStream(BambooHrStream):
    """
    This is not currently in use as per
    https://documentation.bamboohr.com/reference/get-employees-directory-1
    """

    primary_key = "id"  # type: ignore

    def parse_response(
        self,
        response: requests.Response,
        **kwargs,  # type: ignore
    ) -> Iterable[Mapping[str, Any]]:
        yield from response.json()["employees"]

    def path(self, **kwargs) -> str:  # type: ignore
        return "employees/directory"


class SourceBambooHr(AbstractSource):
    @staticmethod
    def _get_authenticator(api_key: str):
        """
        Returns a TokenAuthenticator.

        The API token is concatenated with `:x` and the resulting string is base-64 encoded.
        See https://documentation.bamboohr.com/docs#authentication
        """
        return TokenAuthenticator(
            token=base64.b64encode(f"{api_key}:x".encode("utf-8")).decode("utf-8"),
            auth_method="Basic",
        )

    @staticmethod
    def add_authenticator_to_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds an authenticator entry to the config and returns the config.
        """
        config["authenticator"] = SourceBambooHr._get_authenticator(config["api_key"])
        return config

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        Verifies the config and attempts to fetch the fields from the meta/fields endpoint.
        """
        config = SourceBambooHr.add_authenticator_to_config(cast(Dict[str, Any], config))

        available_fields = MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh)

        try:
            # Check to see that we get some fields back.
            next(available_fields)  # type: ignore
            return True, None
        except StopIteration:
            return False, AvailableFieldsAccessDeniedError()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceBambooHr.add_authenticator_to_config(cast(Dict[str, Any], config))

        # Grabbing these early on and sending them through the config seemed
        # simpler than passing them along as parent streams.
        available_fields: List[str] = (
            list(
                map(
                    lambda field: CustomReportsStream.convert_field_to_id(BambooMetaField(**field)),  # type: ignore
                    MetaFieldsStream(config).read_records(sync_mode=SyncMode.full_refresh),
                )
            )
            + CustomReportsStream.get_default_bamboo_fields()
        )

        available_tables = list(
            map(
                lambda meta_table: TablesStream.convert_raw_meta_table_to_typed(meta_table),  # type: ignore
                MetaTablesStream(config).read_records(sync_mode=SyncMode.full_refresh),
            )
        )

        """
            1. Convert fields in to a list of strings.
            2. Create a function that returns a list of strings.
            3. Just pass that all along.
        """

        config["available_fields"] = available_fields
        config["available_tables"] = available_tables

        return [
            MetaTablesStream(config),
            TablesStream(config),
            MetaFieldsStream(config),
            CustomReportsStream(config),
            # Keeping this around in case we ever need it, but
            # we should be able to get the same data from custom_reports.
            # EmployeesDirectoryStream
        ]
