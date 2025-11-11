import os
from typing import Any, Dict

from fastapi import APIRouter

from ..api_models.capabilities import CapabilitiesResponse

router = APIRouter(
    prefix="/capabilities",
    tags=["capabilities"],
)


@router.get("/", operation_id="getCapabilities")
def get_capabilities() -> CapabilitiesResponse:
    """
    Get the capabilities available for the manifest server.

    Returns:
        Dict containing the service capabilities including custom code execution support.
    """
    # Read the same environment variable as the connector builder server
    enable_unsafe_code = os.getenv("AIRBYTE_ENABLE_UNSAFE_CODE", "false").lower() == "true"

    return CapabilitiesResponse(custom_code_execution=enable_unsafe_code)
