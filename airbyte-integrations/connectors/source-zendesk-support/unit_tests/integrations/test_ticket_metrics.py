# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from datetime import datetime, timezone
from unittest import TestCase
from unittest.mock import patch

import freezegun
import pendulum
from airbyte_cdk.test.mock_http import HttpMocker
from airbyte_cdk.test.mock_http.response_builder import FieldPath
from airbyte_cdk.test.state_builder import StateBuilder
from airbyte_protocol.models import AirbyteStateBlob
from airbyte_protocol.models import Level as LogLevel
from airbyte_protocol.models import SyncMode

from .config import ConfigBuilder
from .helpers import given_post_comments, given_posts, given_ticket_forms
from .utils import datetime_to_string, get_log_messages_by_log_level, read_stream, string_to_datetime
from .zs_requests import TicketMetricsRequestBuilder
from .zs_requests.request_authenticators import ApiTokenAuthenticator
from .zs_responses import ErrorResponseBuilder, TicketMetricsResponseBuilder
from .zs_responses.records import TicketMetricsRecordBuilder

_NOW = datetime.now(timezone.utc)
