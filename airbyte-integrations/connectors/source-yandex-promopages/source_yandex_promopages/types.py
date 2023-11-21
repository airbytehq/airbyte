from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from .auth import CredentialsCraftAuthenticator

Authenticator = TokenAuthenticator | CredentialsCraftAuthenticator
