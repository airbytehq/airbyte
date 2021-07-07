#
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
#

import logging
from pprint import pprint

# %%
import requests

logging.basicConfig(level=logging.DEBUG)

# %%
specification = {
    "client_id": "REPLACE_ME",
    "secret": "REPLACE_ME",
    "start_date": "2021-06-01T00:00:00+00:00",
    "end_date": "2021-06-30T00:00:00+00:00",
    "is_sandbox": True,
}

# %%  READ <client_id> and <secret>

client_id = specification.get("client_id")
secret = specification.get("secret")

# %%  GET API_TOKEN

token_refresh_endpoint = "https://api-m.sandbox.paypal.com/v1/oauth2/token"
data = "grant_type=client_credentials"
headers = {
    "Accept": "application/json",
    "Accept-Language": "en_US",
}

response = requests.request(
    method="POST",
    url=token_refresh_endpoint,
    data=data,
    headers=headers,
    auth=(client_id, secret),
)
response_json = response.json()
print(response_json)
API_TOKEN = response_json["access_token"]

# CREATE TRANSACTIONS
# for i in range(1000):
#     create_response = requests.post(
#         "https://api-m.sandbox.paypal.com/v2/checkout/orders",
#         headers={'content-type': 'application/json', 'authorization': f'Bearer {API_TOKEN}', "prefer": "return=representation"},
#         json={
#             "intent": "CAPTURE",
#             "purchase_units": [
#                 {
#                     "amount": {
#                         "currency_code": "USD",
#                         "value": f"{float(i)}"
#                     }
#                 }
#             ]
#         }
#     )
#
# print(create_response.json())

# %% LIST TRANSACTIONS

url = "https://api-m.sandbox.paypal.com/v1/reporting/transactions"

params = {
    "start_date": "2021-06-20T00:00:00+00:00",
    "end_date": "2021-07-10T07:19:45Z",
    "fields": "all",
    "page_size": "100",
    "page": "1",
}

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}
response = requests.get(
    url,
    headers=headers,
    params=params,
)

pprint(response.json())
