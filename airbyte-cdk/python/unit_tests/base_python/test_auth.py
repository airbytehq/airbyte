# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from airbyte_cdk.base_python import TokenAuthenticator, Oauth2Authenticator


def test_token_authenticator():
    token = TokenAuthenticator("test-token")
    header = token.get_auth_header()
    print(f"{header}")
    assert True


class TestOauth2Authenticator:
    # Test get_auth_header normal

    # Test get_auth_header expired

    # get_refresh_request_body
    def test_refresh_request_body(self):
        scopes = ["scope1", "scope2"]
        oauth = Oauth2Authenticator("refresh_end", "client_id", "client_secret", "refresh_token", scopes)

        body = oauth.get_refresh_request_body()

        expected = {
            "grant_type": "refresh_token",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "refresh_token": "refresh_token",
            "scopes": scopes,
        }

        assert body == expected
