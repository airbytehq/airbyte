#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import concurrent.futures
import datetime
import math
from abc import ABC
from dataclasses import asdict
from http import HTTPStatus
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import urlencode

import requests
import logging

from airbyte_cdk.sources.streams.http import HttpStream

from .api import ZohoAPI
from .exceptions import IncompleteMetaDataException, UnknownDataTypeException
from .types import FieldMeta, ModuleMeta, ZohoPickListItem


# 204 and 304 status codes are valid successful responses,
# but `.json()` will fail because the response body is empty
EMPTY_BODY_STATUSES = (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)

logger = logging.getLogger(__name__)

# Zoho API request to include fields but limit the max fields to 50
FIELDS_MAP = {
    "Contacts": {
        "Name",
        "Owner",
        "Email",
        "Description",
        "currency_symbol",
        "Vendor_Name",
        "Mailing_Zip",
        "Other_Phone",
        "Mailing_State",
        "Twitter",
        "Other_Zip",
        "Mailing_Street",
        "Other_State",
        "Salutation",
        "Other_Country",
        "Last_Activity_Time",
        "First_Name",
        "Full_Name",
        "Asst_Phone",
        "Record_Image",
        "Department",
        "Modified_By",
        "Skype_ID",
        "process_flow",
        "Assistant",
        "Phone",
        "Mailing_Country",
        "Account_Name",
        "id",
        "Email_Opt_Out",
        "approved",
        "Reporting_To",
        "approval",
        "Modified_Time",
        "Date_of_Birth",
        "Mailing_City",
        "Other_City",
        "Created_Time",
        "Title",
        "editable",
        "Other_Street",
        "Mobile",
        "Home_Phone",
        "Last_Name",
        "Lead_Source",
        "Tag",
        "Created_By",
        "Fax",
        "Secondary_Email"
    },
    "Leads": {
        "Name",
        "Owner",
        "Company",
        "Email",
        "Description",
        "currency_symbol",
        "Rating",
        "Website",
        "Twitter",
        "Salutation",
        "Last_Activity_Time",
        "First_Name",
        "Full_Name",
        "Lead_Status",
        "Industry",
        "Record_Image",
        "Modified_By",
        "Skype_ID",
        "converted",
        "process_flow",
        "Phone",
        "Street",
        "Zip_Code",
        "id",
        "Email_Opt_Out",
        "approved",
        "Designation",
        "approval",
        "Modified_Time",
        "Created_Time",
        "editable",
        "City",
        "No_of_Employees",
        "Mobile",
        "Last_Name",
        "State",
        "Lead_Source",
        "Country",
        "Tag",
        "Created_By",
        "Fax",
        "Annual_Revenue",
        "Secondary_Email"
    },
    "Accounts": {
        "Name",
        "Owner",
        "Ownership",
        "Description",
        "currency_symbol",
        "Account_Type",
        "Rating",
        "SIC_Code",
        "Shipping_State",
        "Website",
        "Employees",
        "Last_Activity_Time",
        "Industry",
        "Record_Image",
        "Modified_By",
        "Account_Site",
        "process_flow",
        "Phone",
        "Billing_Country",
        "Account_Name",
        "id",
        "Account_Number",
        "approved",
        "Ticker_Symbol",
        "approval",
        "Modified_Time",
        "Billing_Street",
        "Created_Time",
        "editable",
        "Billing_Code",
        "Parent_Account",
        "Shipping_City",
        "Shipping_Country",
        "Shipping_Code",
        "Billing_City",
        "Billing_State",
        "Tag",
        "Created_By",
        "Fax",
        "Annual_Revenue",
        "Shipping_Street"
    },
}


class ZohoCrmStream(HttpStream, ABC):
    primary_key: str = "id"
    module: ModuleMeta = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if response.status_code in EMPTY_BODY_STATUSES:
            return None
        pagination = response.json()["info"]
        if not pagination["more_records"]:
            return None
        return {"page": pagination["page"] + 1}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = [] if response.status_code in EMPTY_BODY_STATUSES else response.json()["data"]
        yield from data

    def path(self, *args, **kwargs) -> str:
        field_names = ([field.api_name for field in self.module.fields
                        if self.module.api_name not in FIELDS_MAP or field.api_name in FIELDS_MAP[self.module.api_name]]
            if self.module.fields else [])
        query_string = urlencode({"fields": ",".join(field_names)})
        return f"/crm/v8/{self.module.api_name}?{query_string}"

    def get_json_schema(self) -> Optional[Dict[Any, Any]]:
        try:
            return asdict(self.module.schema)
        except IncompleteMetaDataException:
            # to build a schema for a stream, a sequence of requests is made:
            # one `/settings/modules` which introduces a list of modules,
            # one `/settings/modules/{module_name}` per module and
            # one `/settings/fields?module={module_name}` per module.
            # Any of former two can result in 204 and empty body what blocks us
            # from generating stream schema and, therefore, a stream.
            self.logger.warning(
                f"Could not retrieve fields Metadata for module {self.module.api_name}. " f"This stream will not be available for syncs."
            )
            return None
        except UnknownDataTypeException as exc:
            self.logger.warning(f"Unknown data type in module {self.module.api_name}, skipping. Details: {exc}")
            raise


class IncrementalZohoCrmStream(ZohoCrmStream):
    cursor_field = "Modified_Time"

    def __init__(self, authenticator: "requests.auth.AuthBase" = None, config: Mapping[str, Any] = None):
        super().__init__(authenticator)
        self._config = config
        self._state = {}
        self._start_datetime = self._config.get("start_datetime") or "1970-01-01T00:00:00+00:00"

    @property
    def state(self) -> Mapping[str, Any]:
        if not self._state:
            self._state = {self.cursor_field: self._start_datetime}
        return self._state

    @state.setter
    def state(self, value: Mapping[str, Any]):
        self._state = value

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            current_cursor_value = datetime.datetime.fromisoformat(self.state[self.cursor_field])
            latest_cursor_value = datetime.datetime.fromisoformat(record.get(self.cursor_field,'2000-01-01T00:00:00+00:00'))
            new_cursor_value = max(latest_cursor_value, current_cursor_value)
            self.state = {self.cursor_field: new_cursor_value.isoformat("T", "seconds")}
            yield record

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        last_modified = stream_state.get(self.cursor_field, self._start_datetime)
        # since API filters inclusively, we add 1 sec to prevent duplicate reads
        last_modified_dt = datetime.datetime.fromisoformat(last_modified)
        last_modified_dt += datetime.timedelta(seconds=1)
        last_modified = last_modified_dt.isoformat("T", "seconds")
        return {"If-Modified-Since": last_modified}


class ZohoStreamFactory:
    def __init__(self, config: Mapping[str, Any]):
        self.api = ZohoAPI(config)
        self._config = config

    def _init_modules_meta(self) -> List[ModuleMeta]:
        modules_meta_json = self.api.modules_settings()
        modules = [ModuleMeta.from_dict(module) for module in modules_meta_json]
        return list(filter(lambda module: module.api_supported, modules))

    def _populate_fields_meta(self, module: ModuleMeta):
        fields_meta_json = self.api.fields_settings(module.api_name)
        fields_meta = []
        for field in fields_meta_json:
            pick_list_values = field.get("pick_list_values", [])
            if pick_list_values:
                field["pick_list_values"] = [ZohoPickListItem.from_dict(pick_list_item) for pick_list_item in field["pick_list_values"]]
            fields_meta.append(FieldMeta.from_dict(field))
        module.fields = fields_meta

    def _populate_module_meta(self, module: ModuleMeta):
        module_meta_json = self.api.module_settings(module.api_name)
        module.update_from_dict(next(iter(module_meta_json), None))

    def produce(self) -> List[HttpStream]:
        modules = self._init_modules_meta()
        streams = []

        def populate_module(module):
            try:
                self._populate_module_meta(module)
                self._populate_fields_meta(module)

            except Exception:
                logger.exception("Failed while processing module %s", module.api_name)
                return

        def chunk(max_len, lst):
            for i in range(math.ceil(len(lst) / max_len)):
                yield lst[i * max_len : (i + 1) * max_len]

        max_concurrent_request = self.api.max_concurrent_requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_request) as executor:
            for batch in chunk(max_concurrent_request, modules):
                futures = [executor.submit(populate_module, m) for m in batch]
                for fut in futures:
                    fut.result()

        bases = (IncrementalZohoCrmStream,)
        for module in modules:
            stream_cls_attrs = {"url_base": self.api.api_url, "module": module}
            stream_cls_name = f"Incremental{module.api_name}ZohoCRMStream"
            incremental_stream_cls = type(stream_cls_name, bases, stream_cls_attrs)
            stream = incremental_stream_cls(self.api.authenticator, config=self._config)
            if stream.get_json_schema():
                streams.append(stream)

        streams.append(IncrementalUsersZohoCrmStream(self.api.authenticator, config=self._config))
        return streams


class IncrementalUsersZohoCrmStream(IncrementalZohoCrmStream):
    """
    This stream is a special case for the Users module.
    It is not a standard Zoho CRM module and has a different API endpoint.
    """
    module = ModuleMeta(
            api_name="users",
            module_name="Users",
            api_supported=True,
            fields=[
                FieldMeta(api_name="country", data_type="string", json_type="string", display_label="country", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="name_format__s", data_type="string", json_type="string", display_label="name_format__s", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="language", data_type="string", json_type="string", display_label="language", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="microsoft", data_type="boolean", json_type="boolean", display_label="microsoft", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="id", data_type="string", json_type="string", display_label="id", system_mandatory=True, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="state", data_type="string", json_type="string", display_label="state", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="fax", data_type="string", json_type="string", display_label="fax", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="country_locale", data_type="string", json_type="string", display_label="country_locale", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="sandboxDeveloper", data_type="boolean", json_type="boolean", display_label="sandboxDeveloper", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="zip", data_type="string", json_type="string", display_label="zip", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="decimal_separator", data_type="string", json_type="string", display_label="decimal_separator", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="created_time", data_type="string", json_type="string", display_label="created_time", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="time_format", data_type="string", json_type="string", display_label="time_format", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="offset", data_type="string", json_type="string", display_label="offset", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="zuid", data_type="string", json_type="string", display_label="zuid", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="full_name", data_type="string", json_type="string", display_label="full_name", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="phone", data_type="string", json_type="string", display_label="phone", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="dob", data_type="date", json_type="string", display_label="dob", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="sort_order_preference__s", data_type="string", json_type="string", display_label="sort_order_preference__s", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="status", data_type="string", json_type="string", display_label="status", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="type__s", data_type="string", json_type="string", display_label="type__s", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="city", data_type="string", json_type="string", display_label="city", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="signature", data_type="string", json_type="string", display_label="signature", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="locale", data_type="string", json_type="string", display_label="locale", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="personal_account", data_type="boolean", json_type="boolean", display_label="personal_account", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="Isonline", data_type="boolean", json_type="boolean", display_label="Isonline", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="default_tab_group", data_type="string", json_type="string", display_label="default_tab_group", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="street", data_type="string", json_type="string", display_label="street", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="first_name", data_type="string", json_type="string", display_label="first_name", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="email", data_type="string", json_type="string", display_label="email", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="status_reason__s", data_type="string", json_type="string", display_label="status_reason__s", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="website", data_type="string", json_type="string", display_label="website", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="Modified_Time", data_type="string", json_type="string", display_label="Modified_Time", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="mobile", data_type="string", json_type="string", display_label="mobile", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="last_name", data_type="string", json_type="string", display_label="last_name", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="time_zone", data_type="string", json_type="string", display_label="time_zone", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="number_separator", data_type="string", json_type="string", display_label="number_separator", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="confirm", data_type="boolean", json_type="boolean", display_label="confirm", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="date_format", data_type="string", json_type="string", display_label="date_format", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="theme", data_type="object", json_type="jsonobject", display_label="theme", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="customize_info", data_type="object", json_type="jsonobject", display_label="customize_info", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="role", data_type="object", json_type="jsonobject", display_label="role", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="profile", data_type="object", json_type="jsonobject", display_label="profile", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="created_by", data_type="object", json_type="jsonobject", display_label="created_by", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="Modified_By", data_type="object", json_type="jsonobject", display_label="Modified_By", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
                FieldMeta(api_name="Reporting_To", data_type="object", json_type="jsonobject", display_label="Reporting_To", system_mandatory=False, length=None, decimal_place=None, pick_list_values=[]),
            ]
        )

    @property
    def url_base(self) -> str:
        return self.api.api_url

    def path(self, *args, **kwargs) -> str:
        return "/crm/v8/users?type=AllUsers"

    def __init__(self, authenticator: "requests.auth.AuthBase" = None, config: Mapping[str, Any] = None):
        self.api = ZohoAPI(config)
        super().__init__(authenticator, config)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = [] if response.status_code in EMPTY_BODY_STATUSES else response.json()["users"]
        yield from data
