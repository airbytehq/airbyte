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

from pydantic import BaseModel, Field


class AmazonAdsConfig(BaseModel):
    class Config:
        title = "Amazon Ads Spec"

    client_id: str = Field(
        name="Client ID",
        description='Oauth client id <a href="https://advertising.amazon.com/API/docs/en-us/setting-up/step-1-create-lwa-app">How to create your Login with Amazon</a>',
    )
    client_secret: str = Field(
        name="Client secret",
        description='Oauth client secret <a href="https://advertising.amazon.com/API/docs/en-us/setting-up/step-1-create-lwa-app">How to create your Login with Amazon</a>',
        airbyte_secret=True,
    )
    scope: str = Field(
        "advertising::campaign_management",
        name="Client scope",
        examples=[
            "advertising::campaign_management",
            "cpc_advertising:campaign_management",
        ],
        description="By default its advertising::campaign_management, but customers may need to set scope to cpc_advertising:campaign_management.",
    )
    refresh_token: str = Field(
        name="Oauth refresh token",
        description='Oauth 2.0 refresh_token, <a href="https://developer.amazon.com/docs/login-with-amazon/conceptual-overview.html">read details here</a>',
        airbyte_secret=True,
    )

    start_date: str = Field(
        None,
        name="Start date",
        description="Start date for collectiong reports, should not be more than 60 days in past. In YYYY-MM-DD format",
        examples=["2022-10-10", "2022-10-22"],
    )
    host: str = Field(None, alias="_host")

    @classmethod
    def schema(cls, **kvargs):
        schema = super().schema(**kvargs)
        schema["properties"] = {name: desc for name, desc in schema["properties"].items() if not name.startswith("_")}
        return schema
