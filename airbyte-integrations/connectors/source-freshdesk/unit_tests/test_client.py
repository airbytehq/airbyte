"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json

# TODO uncomment once this issue https://github.com/airbytehq/airbyte/issues/1134 to allow depending on local python packages without inheriting
#  Docker images. For now this is covered by standard tests.
# from source_freshdesk.client import Client


def test_fake():
    assert json.loads("{}") == {}


# def test_client_wrong_domain():
#     not_freshdesk_domain = "unknownaccount"
#     expected_error = "Freshdesk v2 API works only via Freshdesk" "domains and not via custom CNAMEs"
#     with pytest.raises(AttributeError, match=expected_error):
#         Client(domain=not_freshdesk_domain, api_key="wrong_key")
#
#
# def test_client_wrong_account():
#     unknown_domain = "unknownaccount.freshdesk.com"
#     client = Client(domain=unknown_domain, api_key="wrong_key")
#     alive, error = client.health_check()
#
#     assert not alive
#     assert error == "Freshdesk Request Failed"
