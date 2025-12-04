#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping, Tuple

from airbyte_cdk.models import AirbyteConnectionStatus, Status
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceAmazonSellerPartner(YamlDeclarativeSource):
    """
    Amazon Seller Partner source connector.
    
    This connector supports both Seller and Vendor account types. The check method
    is overridden to use the appropriate stream for connection testing based on
    the account_type configuration:
    - Seller accounts: Uses the Orders stream (Seller API)
    - Vendor accounts: Uses the VendorOrders stream (Vendor API)
    """

    def __init__(self, catalog: dict | None, config: Mapping[str, Any] | None, state: dict | None, **kwargs: Any):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Check connection to the Amazon Seller Partner API.
        
        Uses the appropriate stream based on account_type:
        - Seller (default): Checks the Orders stream
        - Vendor: Checks the VendorOrders stream
        """
        account_type = config.get("account_type", "Seller")
        
        if account_type == "Vendor":
            stream_name = "VendorOrders"
        else:
            stream_name = "Orders"
        
        # Get all streams and find the one we need to check
        try:
            streams = self.streams(config=config)
            stream_name_to_stream = {s.name: s for s in streams}
            
            if stream_name not in stream_name_to_stream:
                available_streams = list(stream_name_to_stream.keys())
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Stream {stream_name} not found. Available streams: {available_streams}"
                )
            
            stream = stream_name_to_stream[stream_name]
            
            # Check stream availability by attempting to read from it
            try:
                # Use the stream's availability strategy if available
                if hasattr(stream, 'check_availability'):
                    is_available, reason = stream.check_availability(logger, self)
                    if not is_available:
                        return AirbyteConnectionStatus(
                            status=Status.FAILED,
                            message=f"Stream {stream_name} is not available: {reason}"
                        )
                else:
                    # Fallback: try to get at least one record slice to verify connectivity
                    for _ in stream.stream_slices(sync_mode=None):
                        break
                        
            except Exception as e:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Stream {stream_name} is not available: {str(e)}"
                )
            
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"Error checking connection: {str(e)}"
            )
