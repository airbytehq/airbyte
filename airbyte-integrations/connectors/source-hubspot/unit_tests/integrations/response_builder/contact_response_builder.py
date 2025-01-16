# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from airbyte_cdk.test.mock_http import HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template


_CONTACTS_FIELD = "contacts"
_FORM_SUBMISSIONS_FIELD = "form-submissions"
_LIST_MEMBERSHIPS_FIELD = "list-memberships"
_MERGE_AUDITS_FIELD = "merge-audits"


def _get_template() -> Dict[str, Any]:
    return find_template("all_contacts", __file__)


class ContactsListMembershipBuilder:
    def __init__(self) -> None:
        self._template: Dict[str, Any] = _get_template()[_CONTACTS_FIELD][0][_LIST_MEMBERSHIPS_FIELD][0]

    def with_timestamp(self, timestamp: datetime) -> "ContactsListMembershipBuilder":
        self._template["timestamp"] = int(timestamp.timestamp() * 1000)
        return self

    def build(self) -> Dict[str, Any]:
        return self._template


class ContactsMergeAuditsBuilder:
    def __init__(self) -> None:
        self._template: Dict[str, Any] = _get_template()[_CONTACTS_FIELD][0][_MERGE_AUDITS_FIELD][0]

    def with_timestamp(self, timestamp: datetime) -> "ContactsMergeAuditsBuilder":
        self._template["timestamp"] = int(timestamp.timestamp() * 1000)
        return self

    def build(self) -> Dict[str, Any]:
        return self._template


class ContactsFormSubmissionsBuilder:
    def __init__(self) -> None:
        self._template: Dict[str, Any] = _get_template()[_CONTACTS_FIELD][0][_FORM_SUBMISSIONS_FIELD][0]

    def with_timestamp(self, timestamp: datetime) -> "ContactsFormSubmissionsBuilder":
        self._template["timestamp"] = int(timestamp.timestamp() * 1000)
        return self

    def build(self) -> Dict[str, Any]:
        return self._template


class ContactBuilder:
    def __init__(self) -> None:
        self._template: Dict[str, Any] = _get_template()[_CONTACTS_FIELD][0]

    def with_list_memberships(self, memberships: List[ContactsListMembershipBuilder]) -> "ContactBuilder":
        self._template[_LIST_MEMBERSHIPS_FIELD] = [membership.build() for membership in memberships]
        return self

    def with_merge_audits(self, merge_audits: List[ContactsMergeAuditsBuilder]) -> "ContactBuilder":
        self._template[_MERGE_AUDITS_FIELD] = [merge_audit.build() for merge_audit in merge_audits]
        return self

    def with_form_submissions(self, form_submissions: List[ContactsFormSubmissionsBuilder]) -> "ContactBuilder":
        self._template[_FORM_SUBMISSIONS_FIELD] = [form_submission.build() for form_submission in form_submissions]
        return self

    def build(self) -> Dict[str, Any]:
        return self._template


class AllContactsResponseBuilder:
    def __init__(self) -> None:
        self._contacts = []
        self._vid_offset = 0
        self._has_more = False

    def with_contacts(self, contacts: List[ContactBuilder]) -> "AllContactsResponseBuilder":
        self._contacts = [contact.build() for contact in contacts]
        return self

    def with_pagination(self, vid_offset: int) -> "AllContactsResponseBuilder":
        self._has_more = True
        self._vid_offset = vid_offset
        return self

    def build(self) -> HttpResponse:
        template = {
            "contacts": self._contacts,
            "has-more": self._has_more,
            "vid-offset": self._vid_offset,
        }

        return HttpResponse(json.dumps(template), 200)
