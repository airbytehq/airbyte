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

"""
Country	marketplaceId	Country code
Canada	A2EUQ1WTGCTBG2	CA
United States of America	ATVPDKIKX0DER	US
Mexico	A1AM78C64UM0Y8	MX
Brazil	A2Q3Y263D00KWC	BR
Europe

Country	marketplaceId	Country code
Spain	A1RKKUPIHCS9HS	ES
United Kingdom	A1F83G8C2ARO7P	GB
France	A13V1IB3VIYZZH	FR
Netherlands	A1805IZSGTT6HS	NL
Germany	A1PA6795UKMFR9	DE
Italy	APJ6JRA9NG5V4	IT
Sweden	A2NODRKZP88ZB9	SE
Poland	A1C3SOZRARQ6R3	PL
Turkey	A33AVAJ2PDY3EV	TR
United Arab Emirates	A2VIGQ35RCS4UG	AE
India	A21TJRUUN4KGV	IN
Far East

Country	marketplaceId	Country code
Singapore	A19VAU5U5O7RUS	SG
Australia	A39IBJ37TRP1C6	AU
Japan	A1VC38T7YXB528	JP
"""
from enum import Enum


class AWS_ENV(Enum):
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"


def get_aws_base_url(aws_env):
    if aws_env == AWS_ENV.PRODUCTION:
        return "https://sellingpartnerapi"
    return "https://sandbox.sellingpartnerapi"


def get_marketplaces_enum(aws_env):
    base_url = get_aws_base_url(aws_env)

    def __init__(self, endpoint, marketplace_id, region):
        """Easy dot access like: Marketplaces.endpoint ."""

        self.endpoint = endpoint
        self.marketplace_id = marketplace_id
        self.region = region

    values = {
        "AE": (f"{base_url}-eu.amazon.com", "A2VIGQ35RCS4UG", "eu-west-1"),
        "DE": (f"{base_url}-eu.amazon.com", "A1PA6795UKMFR9", "eu-west-1"),
        "PL": (f"{base_url}-eu.amazon.com", "A1C3SOZRARQ6R3", "eu-west-1"),
        "EG": (f"{base_url}-eu.amazon.com", "ARBP9OOSHTCHU", "eu-west-1"),
        "ES": (f"{base_url}-eu.amazon.com", "A1RKKUPIHCS9HS", "eu-west-1"),
        "FR": (f"{base_url}-eu.amazon.com", "A13V1IB3VIYZZH", "eu-west-1"),
        "GB": (f"{base_url}-eu.amazon.com", "A1F83G8C2ARO7P", "eu-west-1"),
        "IN": (f"{base_url}-eu.amazon.com", "A21TJRUUN4KGV", "eu-west-1"),
        "IT": (f"{base_url}-eu.amazon.com", "APJ6JRA9NG5V4", "eu-west-1"),
        "NL": (f"{base_url}-eu.amazon.com", "A1805IZSGTT6HS", "eu-west-1"),
        "SA": (f"{base_url}-eu.amazon.com", "A17E79C6D8DWNP", "eu-west-1"),
        "SE": (f"{base_url}-eu.amazon.com", "A2NODRKZP88ZB9", "eu-west-1"),
        "TR": (f"{base_url}-eu.amazon.com", "A33AVAJ2PDY3EV", "eu-west-1"),
        "UK": (f"{base_url}-eu.amazon.com", "A1F83G8C2ARO7P", "eu-west-1"),  # alias for GB
        "AU": (f"{base_url}-fe.amazon.com", "A39IBJ37TRP1C6", "us-west-2"),
        "JP": (f"{base_url}-fe.amazon.com", "A1VC38T7YXB528", "us-west-2"),
        "SG": (f"{base_url}-fe.amazon.com", "A19VAU5U5O7RUS", "us-west-2"),
        "US": (f"{base_url}-na.amazon.com", "ATVPDKIKX0DER", "us-east-1"),
        "BR": (f"{base_url}-na.amazon.com", "A2Q3Y263D00KWC", "us-east-1"),
        "CA": (f"{base_url}-na.amazon.com", "A2EUQ1WTGCTBG2", "us-east-1"),
        "MX": (f"{base_url}-na.amazon.com", "A1AM78C64UM0Y8", "us-east-1"),
        "__init__": __init__,
    }
    return Enum("Marketplaces", values)
