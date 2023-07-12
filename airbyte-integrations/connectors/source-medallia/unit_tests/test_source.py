from unittest.mock import MagicMock

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from source_medallia.authenticator import Medalliaauth2Authenticator



from source_medallia.source import (
    MedalliaStream,
    Fields,
    FieldId,
    Feedback,
    SourceMedallia,
    initialize_authenticator
)

class TestAuthentication:
    def test_init_oauth2_authentication_init(self, oauth_config):
        oauth_authentication_instance = initialize_authenticator(config=oauth_config)
        assert isinstance(oauth_authentication_instance, Medalliaauth2Authenticator)

    def test_init_oauth2_authentication_wrong_oauth_config_bad_auth_type(self, wrong_oauth_config_bad_auth_type):
        try:
            initialize_authenticator(config=wrong_oauth_config_bad_auth_type)
        except Exception as e:
            assert e.args[0] == "Config validation error. `auth_type` not specified."
