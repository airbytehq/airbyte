#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator

from .streams import CompanyLeaveTypes, Employees, LeaveBalances, LeaveRequests


# Source
class SourceRippling(AbstractSource):
    logger = AirbyteLogger()

    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        try:
            auth = TokenAuthenticator(
                token=config["api_key"],
            )
            employees_stream = Employees(authenticator=auth, filters=config.get("employee_filters", ""))
            employees_stream_gen = employees_stream.read_records(sync_mode=SyncMode.full_refresh)
            next(employees_stream_gen)  # type: ignore
            logger.info("Succesfully connected to Rippling API !")
            return True, None
        except Exception as e:
            logger.error(f"Error while checking : {repr(e)}")
            return (False, f"Could not connect with this access token error: {str(e)}")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(token=config["api_key"])
        return [
            Employees(authenticator=auth, filters=config.get("employee_filters", "")),
            LeaveRequests(authenticator=auth),
            LeaveBalances(authenticator=auth),
            CompanyLeaveTypes(authenticator=auth),
        ]
