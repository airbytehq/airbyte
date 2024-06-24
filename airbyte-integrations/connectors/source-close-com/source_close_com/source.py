#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


class CloseComStream(HttpStream, ABC):
    url_base: str = "https://api.close.com/api/v1/"
    primary_key: str = "id"
    number_of_items_per_page = None
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)

    def __init__(self, **kwargs: Mapping[str, Any]):
        super().__init__(authenticator=kwargs["authenticator"])
        self.config: Mapping[str, Any] = kwargs
        self.start_date: str = kwargs["start_date"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        In one case, Close.com uses two params for pagination: _skip and _limit.
        _skip - number of records from stream data we need skip.
        _limit - number of records in stream, that we received from API.
        For next_page_token need use sum of _skip and _limit values.

        In other case, Close.com uses _cursor param for pagination.
        _cursor - value from API response - cursor_next field.
        """
        decoded_response = response.json()
        has_more = bool(decoded_response.get("has_more", None))
        data = decoded_response.get("data", [])
        cursor_next = decoded_response.get("cursor_next", None)
        if has_more and data:
            parsed = dict(parse_qsl(urlparse(response.url).query))
            # close.com has default skip param - 0. Used for pagination
            skip = parsed.get("_skip", 0)
            limit = parsed.get("_limit", len(data))
            return {"_skip": int(skip) + int(limit)}
        if cursor_next:
            return {"_cursor": cursor_next}
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {}
        if self.number_of_items_per_page:
            params.update({"_limit": self.number_of_items_per_page})

        # Handle pagination by inserting the next page's token in the request parameters
        if next_page_token:
            params.update(next_page_token)

        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """This method is called if we run into the rate limit.
        Close.com puts the retry time in the `rate_reset` response body so
        we return that value. If the response is anything other than a 429 (e.g: 5XX)
        fall back on default retry behavior.
        Rate-reset is the same as retry-after.
        Rate Limits Docs: https://developer.close.com/#ratelimits"""

        backoff_time = None
        error = response.json().get("error", backoff_time)
        if error:
            backoff_time = error.get("rate_reset", backoff_time)
        return backoff_time


class CloseComStreamCustomFields(CloseComStream):
    """Class to get custom fields for close objects that support them."""

    def get_custom_field_schema(self) -> Mapping[str, Any]:
        """Get custom field schema if it exists."""
        resp = requests.request(
            "GET", url=f"{self.url_base}/custom_field/{self.path()}/", headers=self.config["authenticator"].get_auth_header()
        )
        resp.raise_for_status()
        resp_json: Mapping[str, Any] = resp.json()["data"]
        return {f"custom.{data['id']}": {"type": ["null", "string", "number", "boolean"]} for data in resp_json}

    def get_json_schema(self):
        """Override default get_json_schema method to add custom fields to schema."""
        schema = super().get_json_schema()
        schema["properties"].update(self.get_custom_field_schema())
        return schema


class IncrementalCloseComStream(CloseComStream):
    cursor_field = "date_updated"

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Update the state value, default CDK method.
        For example, cursor_field can be "date_updated" or "date_created".
        """
        if not current_stream_state:
            current_stream_state = {self.cursor_field: self.start_date}
        return {self.cursor_field: max(latest_record.get(self.cursor_field, ""), current_stream_state.get(self.cursor_field, ""))}


class IncrementalCloseComStreamCustomFields(CloseComStreamCustomFields, IncrementalCloseComStream):
    """Class to get custom fields for close objects using incremental stream."""


class CloseComActivitiesStream(IncrementalCloseComStream):
    """
    General class for activities. Define request params based on cursor_field value.
    """

    cursor_field = "date_created"
    number_of_items_per_page = 100

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["date_created__gte"] = stream_state.get(self.cursor_field)
        return params

    def path(self, **kwargs) -> str:
        return f"activity/{self._type}"


class CreatedActivities(CloseComActivitiesStream):
    """
    Get created activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-created-activities
    """

    _type = "created"


class NoteActivities(CloseComActivitiesStream):
    """
    Get note activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-note-activities
    """

    _type = "note"


class EmailThreadActivities(CloseComActivitiesStream):
    """
    Get email thread activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-emailthread-activities
    """

    _type = "emailthread"


class EmailActivities(CloseComActivitiesStream):
    """
    Get email activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-email-activities
    """

    _type = "email"


class SmsActivities(CloseComActivitiesStream):
    """
    Get SMS activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-sms-activities
    """

    _type = "sms"


class CallActivities(CloseComActivitiesStream):
    """
    Get call activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-call-activities
    """

    _type = "call"


class MeetingActivities(CloseComActivitiesStream):
    """
    Get meeting activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-meeting-activities
    """

    _type = "meeting"


class LeadStatusChangeActivities(CloseComActivitiesStream):
    """
    Get lead status change activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-leadstatuschange-activities
    """

    _type = "status_change/lead"


class OpportunityStatusChangeActivities(CloseComActivitiesStream):
    """
    Get opportunity status change activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-opportunitystatuschange-activities
    """

    _type = "status_change/opportunity"


class TaskCompletedActivities(CloseComActivitiesStream):
    """
    Get task completed activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-taskcompleted-activities
    """

    _type = "task_completed"


class Events(IncrementalCloseComStream):
    """
    Get events on a specific date
    API Docs: https://developer.close.com/#event-log-retrieve-a-list-of-events
    """

    number_of_items_per_page = 50

    def path(self, **kwargs) -> str:
        return "event"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["date_updated__gte"] = stream_state.get(self.cursor_field)
        return params


class Leads(IncrementalCloseComStreamCustomFields):
    """
    Get leads on a specific date
    API Docs: https://developer.close.com/#leads
    """

    number_of_items_per_page = 200

    def path(self, **kwargs) -> str:
        return "lead"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["query"] = f"sort:updated date_updated >= {stream_state.get(self.cursor_field)}"
        return params


class CloseComTasksStream(IncrementalCloseComStream):
    """
    General class for tasks. Define request params based on _type value.
    """

    cursor_field = "date_created"
    number_of_items_per_page = 1000

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["_type"] = self._type
        params["_order_by"] = self.cursor_field
        if stream_state.get(self.cursor_field):
            params["date_created__gte"] = stream_state.get(self.cursor_field)
        return params

    def path(self, **kwargs) -> str:
        return "task"


class LeadTasks(CloseComTasksStream):
    """
    Get lead tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "lead"


class IncomingEmailTasks(CloseComTasksStream):
    """
    Get incoming email tasks on a specific date
    API Docs: https://developer.close.com/#tasks
    """

    _type = "incoming_email"


class EmailFollowupTasks(CloseComTasksStream):
    """
    Get email followup tasks on a specific date
    API Docs: https://developer.close.com/#tasks
    """

    _type = "email_followup"


class MissedCallTasks(CloseComTasksStream):
    """
    Get missed call tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "missed_call"


class AnsweredDetachedCallTasks(CloseComTasksStream):
    """
    Get answered detached call tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "answered_detached_call"


class VoicemailTasks(CloseComTasksStream):
    """
    Get voicemail tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "voicemail"


class OpportunityDueTasks(CloseComTasksStream):
    """
    Get opportunity due tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "opportunity_due"


class IncomingSmsTasks(CloseComTasksStream):
    """
    Get incoming SMS tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    _type = "incoming_sms"


class CloseComCustomFieldsStream(CloseComStream):
    """
    General class for custom fields. Define path based on _type value.
    """

    number_of_items_per_page = 1000

    def path(self, **kwargs) -> str:
        return f"custom_field/{self._type}"


class LeadCustomFields(CloseComCustomFieldsStream):
    """
    Get lead custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-lead-custom-fields-for-your-organization
    """

    _type = "lead"


class ContactCustomFields(CloseComCustomFieldsStream):
    """
    Get contact custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-contact-custom-fields-for-your-organization
    """

    _type = "contact"


class OpportunityCustomFields(CloseComCustomFieldsStream):
    """
    Get opportunity custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-opportunity-custom-fields-for-your-organization
    """

    _type = "opportunity"


class ActivityCustomFields(CloseComCustomFieldsStream):
    """
    Get activity custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-activity-custom-fields-for-your-organization
    """

    _type = "activity"


class Users(CloseComStream):
    """
    Get users for Close.com account organization
    API Docs: https://developer.close.com/#users
    """

    number_of_items_per_page = 1000

    def path(self, **kwargs) -> str:
        return "user"


class Contacts(CloseComStreamCustomFields):
    """
    Get contacts for Close.com account organization
    API Docs: https://developer.close.com/#contacts
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return "contact"


class Opportunities(IncrementalCloseComStreamCustomFields):
    """
    Get opportunities on a specific date
    API Docs: https://developer.close.com/#opportunities
    """

    cursor_field = "date_updated"
    number_of_items_per_page = 250

    def path(self, **kwargs) -> str:
        return "opportunity"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["_order_by"] = self.cursor_field
        if stream_state.get(self.cursor_field):
            params["date_updated__gte"] = stream_state.get(self.cursor_field)
        return params


class Roles(CloseComStream):
    """
    Get roles for Close.com account organization
    API Docs: https://developer.close.com/#roles
    """

    def path(self, **kwargs) -> str:
        return "role"


class LeadStatuses(CloseComStream):
    """
    Get lead statuses for Close.com account organization
    API Docs: https://developer.close.com/#lead-statuses
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return "status/lead"


class OpportunityStatuses(CloseComStream):
    """
    Get opportunity statuses for Close.com account organization
    API Docs: https://developer.close.com/#opportunity-statuses
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return "status/opportunity"


class Pipelines(CloseComStream):
    """
    Get pipelines for Close.com account organization
    API Docs: https://developer.close.com/#pipelines
    """

    def path(self, **kwargs) -> str:
        return "pipeline"


class EmailTemplates(CloseComStream):
    """
    Get email templates for Close.com account organization
    API Docs: https://developer.close.com/#email-templates
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return "email_template"


class CloseComConnectedAccountsStream(CloseComStream):
    """
    General class for connected accounts. Define request params based on _type value.
    """

    number_of_items_per_page = 100

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["_type"] = self._type
        return params

    def path(self, **kwargs) -> str:
        return "connected_account"


class GoogleConnectedAccounts(CloseComConnectedAccountsStream):
    """
    Get google connected accounts for Close.com account
    API Docs: https://developer.close.com/#connected-accounts
    """

    _type = "google"


class CustomEmailConnectedAccounts(CloseComConnectedAccountsStream):
    """
    Get custom email connected accounts for Close.com account
    API Docs: https://developer.close.com/#connected-accounts
    """

    _type = "custom_email"


class ZoomConnectedAccounts(CloseComConnectedAccountsStream):
    """
    Get zoom connected accounts for Close.com account
    API Docs: https://developer.close.com/#connected-accounts
    """

    _type = "zoom"


class SendAs(CloseComStream):
    """
    Get Send As Associations by allowing or allowed user for Close.com
    API Docs: https://developer.close.com/#send-as
    """

    def path(self, **kwargs) -> str:
        return "send_as"


class EmailSequences(CloseComStream):
    """
    Get Email Sequences - series of emails to be sent, one by one, in specified time gaps to specific subscribers until
    they reply.
    API Docs: https://developer.close.com/#email-sequences
    """

    number_of_items_per_page = 1000

    def path(self, **kwargs) -> str:
        return "sequence"


class Dialer(CloseComStream):
    """
    Get dialer sessions for Close.com account organization
    API Docs: https://developer.close.com/#dialer
    """

    def path(self, **kwargs) -> str:
        return "dialer"


class SmartViews(CloseComStream):
    """
    Get smart view. Smart Views are "saved search queries" in Close and show up in the sidebar in the UI.
    They can be private for a user or shared with an entire Organization.
    API Docs: https://developer.close.com/#dialer
    """

    number_of_items_per_page = 600

    def path(self, **kwargs) -> str:
        return "saved_search"


class CloseComBulkActionsStream(CloseComStream):
    """
    General class for Bulk Actions. Define path based on _type value.
    Bulk actions are used to perform an "action" (send an email, update a lead status, etc.) on a number of leads
    all at once based on a Lead search query.
    API Docs: https://developer.close.com/#bulk-actions
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return f"bulk_action/{self._type}"


class EmailBulkActions(CloseComBulkActionsStream):
    """
    Get all email bulk actions of Close.com organization.
    API Docs: https://developer.close.com/#bulk-actions-list-bulk-emails
    """

    _type = "email"


class SequenceSubscriptionBulkActions(CloseComBulkActionsStream):
    """
    Get all sequence subscription bulk actions of Close.com organization.
    API Docs: https://developer.close.com/#bulk-actions-list-bulk-sequence-subscriptions
    """

    _type = "sequence_subscription"


class DeleteBulkActions(CloseComBulkActionsStream):
    """
    Get all bulk deletes actions of Close.com organization.
    API Docs: https://developer.close.com/#bulk-actions-list-bulk-deletes
    """

    _type = "delete"


class EditBulkActions(CloseComBulkActionsStream):
    """
    Get all bulk edits actions of Close.com organization.
    API Docs: https://developer.close.com/#bulk-actions-list-bulk-edits
    """

    _type = "edit"


class IntegrationLinks(CloseComStream):
    """
    Get all integration links of Close.com organization.
    API Docs: https://developer.close.com/#integration-links
    """

    number_of_items_per_page = 100

    def path(self, **kwargs) -> str:
        return "integration_link"


class CustomActivities(CloseComStream):
    """
    Get all Custom Activities of Close.com organization.
    API Docs: https://developer.close.com/#custom-activities
    """

    def path(self, **kwargs) -> str:
        return "custom_activity"


class Base64HttpAuthenticator(TokenAuthenticator):
    """
    :auth - tuple with (api_key as username, password string). Password should be empty.
    https://developer.close.com/#authentication
    """

    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic"):
        auth_string = f"{auth[0]}:{auth[1]}".encode("latin1")
        b64_encoded = b64encode(auth_string).decode("ascii")
        super().__init__(token=b64_encoded, auth_method=auth_method)


class SourceCloseCom(AbstractSource):
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            authenticator = Base64HttpAuthenticator(auth=(config["api_key"], "")).get_auth_header()
            url = "https://api.close.com/api/v1/me"
            response = requests.request("GET", url=url, headers=authenticator)
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        authenticator = Base64HttpAuthenticator(auth=(config["api_key"], ""))
        args = {"authenticator": authenticator, "start_date": config["start_date"]}
        return [
            CreatedActivities(**args),
            OpportunityStatusChangeActivities(**args),
            NoteActivities(**args),
            MeetingActivities(**args),
            CallActivities(**args),
            EmailActivities(**args),
            EmailThreadActivities(**args),
            LeadStatusChangeActivities(**args),
            SmsActivities(**args),
            TaskCompletedActivities(**args),
            Leads(**args),
            LeadTasks(**args),
            IncomingEmailTasks(**args),
            EmailFollowupTasks(**args),
            MissedCallTasks(**args),
            AnsweredDetachedCallTasks(**args),
            VoicemailTasks(**args),
            OpportunityDueTasks(**args),
            IncomingSmsTasks(**args),
            Events(**args),
            LeadCustomFields(**args),
            ContactCustomFields(**args),
            OpportunityCustomFields(**args),
            ActivityCustomFields(**args),
            Users(**args),
            Contacts(**args),
            Opportunities(**args),
            Roles(**args),
            LeadStatuses(**args),
            OpportunityStatuses(**args),
            Pipelines(**args),
            EmailTemplates(**args),
            GoogleConnectedAccounts(**args),
            CustomEmailConnectedAccounts(**args),
            ZoomConnectedAccounts(**args),
            SendAs(**args),
            EmailSequences(**args),
            Dialer(**args),
            SmartViews(**args),
            EmailBulkActions(**args),
            SequenceSubscriptionBulkActions(**args),
            DeleteBulkActions(**args),
            EditBulkActions(**args),
            IntegrationLinks(**args),
            CustomActivities(**args),
        ]
