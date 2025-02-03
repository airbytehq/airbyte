from pydantic import BaseModel, Field, Extra

class Arbitrary(BaseModel):
    class Config:
        extra = Extra.allow

class AccountLookupFailed(Exception):
    pass

class LookupConfig(BaseModel):

    url: str = Field(
        title="Endoint URL",
        description="The URL to fetch the list",
    )
    method: str = Field(
        title="HTTP method to use",
        description="e.g. GET, POST, PUT, DELETE, HEAD, OPTIONS, TRACE",
    )
    bearer_token: str = Field(
        title="Bearer token",
        description="Token to authenticate against the API",
        airbyte_secret=True,
    )
    headers: Arbitrary = Field(
        title="Additional HTTP headers",
        description="HTTP headers to add to the request",
        default_factory=dict
    )
    payload: Arbitrary = Field(
        title="HTTP payload",
        description="Map of the json payload to submit to the endpoint",
        default_factory=dict,
    )
    path: str = Field(
        title="Path",
        description="Path to extract the relevant list from the response JSON",
    )