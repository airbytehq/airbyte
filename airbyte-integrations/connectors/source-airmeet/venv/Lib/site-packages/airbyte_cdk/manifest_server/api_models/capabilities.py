from pydantic import BaseModel


class CapabilitiesResponse(BaseModel):
    """Capabilities of the manifest server."""

    custom_code_execution: bool
