from typing import TypedDict, Dict, Literal

Region = Literal["standard", "us", "aus"]
Environment = Literal["production", "staging"]


class InputConfig(TypedDict):
    clientId: str  # Assuming that it is required to match the pattern
    clientSecret: str  # Assuming that it is required to match the pattern
    environment: Literal["staging", "production"]
    region: Literal["standard", "us", "aus"]


class EndpointDetails(TypedDict):
    app: str
    auth: str
    api: str


EnvironmentMapping = Dict[Environment, EndpointDetails]
EndpointMapping = Dict[Region, EnvironmentMapping]

ENDPOINTS: EndpointMapping = {
    "standard": {
        "production": {
            "app": "https://app.firstresonance.io",
            "auth": "https://auth.buildwithion.com",
            "api": "https://api.buildwithion.com",
        },
        "staging": {
            "app": "https://staging.firstresonance.io",
            "auth": "https://staging-auth.buildwithion.com",
            "api": "https://staging-api.buildwithion.com",
        },
    },
    "us": {
        "production": {"app": "https://app.ion-gov.com", "auth": "https://auth.ion-gov.com", "api": "https://api.ion-gov.com"},
        "staging": {
            "auth": "https://staging.ion-gov.com",
            "app": "https://auth-staging-gov.buildwithion.com",
            "api": "https://staging-api.ion-gov.com",
        },
    },
    "aus": {
        "production": {
            "auth": "app.ion-aus.com",
            "app": "auth-production-aus.buildwithion.com",
            "api": "https://api-production-aus.buildwithion.com",
        },
        "staging": {
            "app": "https://app.ion-aus.com",
            "auth": "https://auth-staging-aus.buildwithion.com",
            "api": "https://api-staging-aus.buildwithion.com",
        },
    },
}
