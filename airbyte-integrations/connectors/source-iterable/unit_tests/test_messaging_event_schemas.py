#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import pytest
from source_iterable.streams import (
    InAppClick,
    InAppClose,
    InAppDelete,
    InAppDelivery,
    InAppOpen,
    InAppSend,
    InAppSendSkip,
    IterableExportEventsStreamAdjustableRange,
    PushBounce,
    PushOpen,
    PushSend,
    PushSendSkip,
    PushUninstall,
    WebPushClick,
    WebPushSend,
    WebPushSendSkip,
)

from airbyte_cdk.sources.streams.core import package_name_from_class
from airbyte_cdk.sources.utils.schema_helpers import ResourceSchemaLoader


MESSAGING_EVENT_STREAMS = [
    PushSend,
    PushSendSkip,
    PushOpen,
    PushUninstall,
    PushBounce,
    WebPushSend,
    WebPushClick,
    WebPushSendSkip,
    InAppSend,
    InAppOpen,
    InAppClick,
    InAppClose,
    InAppDelete,
    InAppDelivery,
    InAppSendSkip,
]

# Fields that identify which message was sent; the export API returns them as top-level properties.
MESSAGE_IDENTIFIERS = {"campaignId", "templateId", "messageId"}


def _schema(stream_class):
    return stream_class(authenticator=None, start_date="2019-10-10T00:00:00").get_json_schema()


@pytest.mark.parametrize("stream_class", MESSAGING_EVENT_STREAMS, ids=lambda c: c.__name__)
def test_messaging_event_stream_declares_message_identifiers(stream_class):
    """Fields missing from the declared schema are dropped by destinations that materialize only
    declared columns, so campaignId/templateId/messageId must be declared explicitly."""
    assert not issubclass(stream_class, IterableExportEventsStreamAdjustableRange)
    assert MESSAGE_IDENTIFIERS <= set(_schema(stream_class)["properties"])


@pytest.mark.parametrize("stream_class", MESSAGING_EVENT_STREAMS, ids=lambda c: c.__name__)
def test_messaging_event_schema_is_superset_of_generic_events_schema(stream_class):
    """Moving off the generic 'events' schema must not remove any previously declared column."""
    events = ResourceSchemaLoader(package_name_from_class(IterableExportEventsStreamAdjustableRange)).get_schema("events")
    assert set(events["properties"]) <= set(_schema(stream_class)["properties"])
