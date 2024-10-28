#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from freezegun import freeze_time
from source_google_analytics_data_api.authenticator import GoogleServiceKeyAuthenticator


@freeze_time("2023-01-01 00:00:00")
def test_token_rotation(requests_mock):
    credentials = {
        "client_email": "client_email",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIBVQIBADANBgkqhkiG9w0BAQEFAASCAT8wggE7AgEAAkEA3slcXL+dA36ESmOi\n1xBhZmp5Hn0WkaHDtW4naba3plva0ibloBNWhFhjQOh7Ff01PVjhT4D5jgqXBIgc\nz9Gv3QIDAQABAkEArlhYPoD5SB2/O1PjwHgiMPrL1C9B9S/pr1cH4vPJnpY3VKE3\n5hvdil14YwRrcbmIxMkK2iRLi9lM4mJmdWPy4QIhAPsRFXZSGx0TZsDxD9V0ZJmZ\n0AuDCj/NF1xB5KPLmp7pAiEA4yoFox6w7ql/a1pUVaLt0NJkDfE+22pxYGNQaiXU\nuNUCIQCsFLaIJZiN4jlgbxlyLVeya9lLuqIwvqqPQl6q4ad12QIgS9gG48xmdHig\n8z3IdIMedZ8ZCtKmEun6Cp1+BsK0wDUCIF0nHfSuU+eTQ2qAON2SHIrJf8UeFO7N\nzdTN1IwwQqjI\n-----END PRIVATE KEY-----\n",
        "client_id": "client_id",
    }
    authenticator = GoogleServiceKeyAuthenticator(credentials)

    auth_request = requests_mock.register_uri(
        "POST", authenticator._google_oauth2_token_endpoint, json={"access_token": "bearer_token", "expires_in": 3600}
    )

    authenticated_request = authenticator(requests.Request())
    assert auth_request.call_count == 1
    assert auth_request.last_request.qs.get("assertion") == [
        "eyjhbgcioijsuzi1niisimtpzci6imnsawvudf9pzcisinr5cci6ikpxvcj9.eyjpc3mioijjbgllbnrfzw1hawwilcjzy29wzsi6imh0dhbzoi8vd3d3lmdvb2dszwfwaxmuy29tl2f1dggvyw5hbhl0awnzlnjlywrvbmx5iiwiyxvkijoiahr0chm6ly9vyxv0adiuz29vz2xlyxbpcy5jb20vdg9rzw4ilcjlehaioje2nzi1mzq4mdasimlhdci6mty3mjuzmtiwmh0.oy_do4cxytjclgajcutbolxftlba89bt2ipuegmis7crh9no_q9h4ispv7iquz5d5h58tpftjhdayb5jfuvheq"
    ]
    assert auth_request.last_request.qs.get("grant_type") == ["urn:ietf:params:oauth:grant-type:jwt-bearer"]
    assert authenticator._token.get("expires_at") == 1672534800
    assert authenticated_request.headers.get("Authorization") == "Bearer bearer_token"
