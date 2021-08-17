#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from abc import ABC
from base64 import b64encode
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class CloseComStream(HttpStream, ABC):
    url_base: str = "https://api.close.com/api/v1/"
    primary_key: str = "id"
    number_of_items_per_page: int = 100

    def __init__(self, **kwargs: Mapping[str, Any]):
        super().__init__(authenticator=kwargs["authenticator"])
        self.config: Mapping[str, Any] = kwargs
        self.start_date: str = kwargs["start_date"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        decoded_response = response.json()
        has_more = bool(decoded_response.get("has_more", None))
        data = decoded_response.get("data", [])
        if has_more and data:
            parsed = dict(parse_qsl(urlparse(response.url).query))
            # close.com has default skip param - 0. Used for pagination
            skip = parsed.get("_skip", 0)
            limit = parsed.get("_limit", self.number_of_items_per_page)
            return {"_skip": int(skip) + int(limit)}
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = {"_limit": self.number_of_items_per_page}

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
        Rate Limits Docs: https://developer.close.com/#ratelimits"""

        return response.json().get("error", {}).get("rate_reset", 0)


class IncrementalCloseComStream(CloseComStream):
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


class CloseComActivitiesMixin(IncrementalCloseComStream):
    """
    General class for activities. Define request params based on cursor_field value.
    """

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["date_created__gt"] = stream_state.get(self.cursor_field)
        return params


class CreatedActivities(CloseComActivitiesMixin):
    """
    Get created activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-created-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/created"


class NoteActivities(CloseComActivitiesMixin):
    """
    Get note activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-note-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/note"


class EmailThreadActivities(CloseComActivitiesMixin):
    """
    Get email thread activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-emailthread-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/emailthread"


class EmailActivities(CloseComActivitiesMixin):
    """
    Get email activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-email-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/email"


class SmsActivities(CloseComActivitiesMixin):
    """
    Get SMS activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-sms-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/sms"


class CallActivities(CloseComActivitiesMixin):
    """
    Get call activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-call-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/call"


class MeetingActivities(CloseComActivitiesMixin):
    """
    Get meeting activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-meeting-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/meeting"


class LeadStatusChangeActivities(CloseComActivitiesMixin):
    """
    Get lead status change activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-leadstatuschange-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/status_change/lead"


class OpportunityStatusChangeActivities(CloseComActivitiesMixin):
    """
    Get opportunity status change activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-opportunitystatuschange-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/status_change/opportunity"


class TaskCompletedActivities(CloseComActivitiesMixin):
    """
    Get task completed activities on a specific date
    API Docs: https://developer.close.com/#activities-list-or-filter-all-taskcompleted-activities
    """

    cursor_field = "date_created"

    def path(self, **kwargs) -> str:
        return "activity/task_completed"


class Events(IncrementalCloseComStream):
    """
    Get events on a specific date
    API Docs: https://developer.close.com/#event-log-retrieve-a-list-of-events
    """

    cursor_field = "date_updated"
    number_of_items_per_page = 50

    def path(self, **kwargs) -> str:
        return "event"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["date_updated__gt"] = stream_state.get(self.cursor_field)
        return params


class Leads(IncrementalCloseComStream):
    """
    Get leads on a specific date
    API Docs: https://developer.close.com/#leads
    """

    cursor_field = "date_updated"

    def path(self, **kwargs) -> str:
        return "lead"

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        if stream_state.get(self.cursor_field):
            params["query"] = f"date_updated > {stream_state.get(self.cursor_field)}"
        return params


class CloseComTasksMixin(IncrementalCloseComStream):
    """
    General class for tasks. Define request params based on _type value.
    """

    def request_params(self, stream_state=None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["_type"] = self._type
        if stream_state.get(self.cursor_field):
            params["date_created__gt"] = stream_state.get(self.cursor_field)
        return params


class LeadTasks(CloseComTasksMixin):
    """
    Get lead tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "lead"

    def path(self, **kwargs) -> str:
        return "task"


class IncomingEmailTasks(CloseComTasksMixin):
    """
    Get incoming email tasks on a specific date
    API Docs: https://developer.close.com/#tasks
    """

    cursor_field = "date_created"
    _type = "incoming_email"

    def path(self, **kwargs) -> str:
        return "task"


class EmailFollowupTasks(CloseComTasksMixin):
    """
    Get email followup tasks on a specific date
    API Docs: https://developer.close.com/#tasks
    """

    cursor_field = "date_created"
    _type = "email_followup"

    def path(self, **kwargs) -> str:
        return "task"


class MissedCallTasks(CloseComTasksMixin):
    """
    Get missed call tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "missed_call"

    def path(self, **kwargs) -> str:
        return "task"


class AnsweredDetachedCallTasks(CloseComTasksMixin):
    """
    Get answered detached call tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "answered_detached_call"

    def path(self, **kwargs) -> str:
        return "task"


class VoicemailTasks(CloseComTasksMixin):
    """
    Get voicemail tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "voicemail"

    def path(self, **kwargs) -> str:
        return "task"


class OpportunityDueTasks(CloseComTasksMixin):
    """
    Get opportunity due tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "opportunity_due"

    def path(self, **kwargs) -> str:
        return "task"


class IncomingSmsTasks(CloseComTasksMixin):
    """
    Get incoming SMS tasks on a specific date
    API Docs: https://developer.close.com/#task
    """

    cursor_field = "date_created"
    _type = "incoming_sms"

    def path(self, **kwargs) -> str:
        return "task"


class LeadCustomFields(CloseComStream):
    """
    Get lead custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-lead-custom-fields-for-your-organization
    """

    def path(self, **kwargs) -> str:
        return "custom_field/lead"


class ContactCustomFields(CloseComStream):
    """
    Get contact custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-contact-custom-fields-for-your-organization
    """

    def path(self, **kwargs) -> str:
        return "custom_field/contact"


class OpportunityCustomFields(CloseComStream):
    """
    Get opportunity custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-opportunity-custom-fields-for-your-organization
    """

    def path(self, **kwargs) -> str:
        return "custom_field/opportunity"


class ActivityCustomFields(CloseComStream):
    """
    Get activity custom fields for Close.com account organization
    API Docs: https://developer.close.com/#custom-fields-list-all-the-activity-custom-fields-for-your-organization
    """

    def path(self, **kwargs) -> str:
        return "custom_field/activity"


class Users(CloseComStream):
    """
    Get users for Close.com account organization
    API Docs: https://developer.close.com/#users
    """

    def path(self, **kwargs) -> str:
        return "user"


class Base64HttpAuthenticator(TokenAuthenticator):
    def __init__(self, auth: Tuple[str, str], auth_method: str = "Basic", **kwargs):
        auth_string = f"{auth[0]}:{auth[1]}".encode("latin1")
        b64_encoded = b64encode(auth_string).decode("ascii")
        super().__init__(token=b64_encoded, auth_method=auth_method, **kwargs)


class SourceCloseCom(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            url = "https://api.close.com/api/v1/me"
            response = requests.request(
                "GET",
                url=url,
                auth=(config["api_key"], ""),
            )
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
        ]
