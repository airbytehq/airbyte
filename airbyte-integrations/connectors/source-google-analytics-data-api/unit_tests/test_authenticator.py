import datetime

from source_google_analytics_data_api import utils
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator


TEST_PRIVATE_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIIBPAIBAAJBAIy64eoS8VCwNnu6+kcyvRc7w/Cw20fnZWcpftLIl33ZWdXl/Q+W
sEQkm2RRWO2R9CGC2bJRZYEbiAabuG4T1LkCAwEAAQJBAIbr5Qv1fUZOqu2VJb58
9qz/r6ti49jcEGwHbH/JsPQFpXWTyKdonibIblLDB4AbZdR25zEM2k2G42OErWjJ
0wECIQD21o4uOMJtAe7GLvg3AeQrb4t9sWlCPuNNxnmKfn8PfQIhAJH0F7vSyD7D
UwRcMht0PU65zWUZArBaI7BlpmFhgNbtAiEA1rIZ6vQtkDjtIW37MYUwm+Milgo4
vokKljx6vM5339UCIEb1Owyvn3cUEypNgHbkfmHl5zu9exct26gI42j4tGDJAiEA
3uFuRTUY3W5s8hxyHcATsGhWfGa4VCSjlKE+sSchksc=
-----END RSA PRIVATE KEY-----
"""


def test_authenticator(mocker):
    requests = mocker.MagicMock()
    requests.request.return_value.json.side_effect = [
        {
            "expires_in": GoogleServiceKeyAuthenticator._default_token_lifetime_secs,
            "access_token": "ga-access-token-1"
        },
        {
            "expires_in": GoogleServiceKeyAuthenticator._default_token_lifetime_secs,
            "access_token": "ga-access-token-2"
        }
    ]

    mocker.patch("source_google_analytics_data_api.authenticator.requests", requests)

    authenticator = GoogleServiceKeyAuthenticator(credentials={
        "client_email": "example-app@airbyte.com",
        "private_key": TEST_PRIVATE_KEY,
        "client_id": "c-airbyte-001"
    })

    request_object = mocker.MagicMock()
    request_object.headers = {}

    authenticator(request_object)
    assert requests.request.call_count == 1
    assert request_object.headers["Authorization"] == f"Bearer ga-access-token-1"

    authenticator(request_object)
    assert requests.request.call_count == 1
    assert request_object.headers["Authorization"] == f"Bearer ga-access-token-1"

    authenticator._token["expires_at"] = utils.datetime_to_secs(datetime.datetime.utcnow()) - GoogleServiceKeyAuthenticator._default_token_lifetime_secs

    authenticator(request_object)
    assert requests.request.call_count == 2
    assert request_object.headers["Authorization"] == f"Bearer ga-access-token-2"
