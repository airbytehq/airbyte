#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
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
Belgium	AMEN7PMS3EDWL	BE
Far East

Country	marketplaceId	Country code
Singapore	A19VAU5U5O7RUS	SG
Australia	A39IBJ37TRP1C6	AU
Japan	A1VC38T7YXB528	JP
"""
from enum import Enum
from typing import Dict, Tuple


class AWSEnvironment(str, Enum):
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"


class AWSRegion(str, Enum):
    AE = "AE"
    AU = "AU"
    BE = "BE"
    BR = "BR"
    CA = "CA"
    DE = "DE"
    EG = "EG"
    ES = "ES"
    FR = "FR"
    GB = "GB"
    IN = "IN"
    IT = "IT"
    JP = "JP"
    MX = "MX"
    NL = "NL"
    PL = "PL"
    SA = "SA"
    SE = "SE"
    SG = "SG"
    TR = "TR"
    UK = "UK"
    US = "US"


def get_aws_base_url(aws_env: AWSEnvironment) -> str:
    if aws_env == AWSEnvironment.PRODUCTION:
        return "https://sellingpartnerapi"
    return "https://sandbox.sellingpartnerapi"


def get_marketplaces(aws_env: AWSEnvironment) -> Dict[AWSRegion, Tuple[str, str, str]]:
    base_url = get_aws_base_url(aws_env)

    marketplaces = {
        AWSRegion.AE: (f"{base_url}-eu.amazon.com", "A2VIGQ35RCS4UG", "eu-west-1"),
        AWSRegion.DE: (f"{base_url}-eu.amazon.com", "A1PA6795UKMFR9", "eu-west-1"),
        AWSRegion.PL: (f"{base_url}-eu.amazon.com", "A1C3SOZRARQ6R3", "eu-west-1"),
        AWSRegion.EG: (f"{base_url}-eu.amazon.com", "ARBP9OOSHTCHU", "eu-west-1"),
        AWSRegion.ES: (f"{base_url}-eu.amazon.com", "A1RKKUPIHCS9HS", "eu-west-1"),
        AWSRegion.FR: (f"{base_url}-eu.amazon.com", "A13V1IB3VIYZZH", "eu-west-1"),
        AWSRegion.IN: (f"{base_url}-eu.amazon.com", "A21TJRUUN4KGV", "eu-west-1"),
        AWSRegion.IT: (f"{base_url}-eu.amazon.com", "APJ6JRA9NG5V4", "eu-west-1"),
        AWSRegion.NL: (f"{base_url}-eu.amazon.com", "A1805IZSGTT6HS", "eu-west-1"),
        AWSRegion.SA: (f"{base_url}-eu.amazon.com", "A17E79C6D8DWNP", "eu-west-1"),
        AWSRegion.SE: (f"{base_url}-eu.amazon.com", "A2NODRKZP88ZB9", "eu-west-1"),
        AWSRegion.TR: (f"{base_url}-eu.amazon.com", "A33AVAJ2PDY3EV", "eu-west-1"),
        AWSRegion.UK: (f"{base_url}-eu.amazon.com", "A1F83G8C2ARO7P", "eu-west-1"),
        AWSRegion.AU: (f"{base_url}-fe.amazon.com", "A39IBJ37TRP1C6", "us-west-2"),
        AWSRegion.JP: (f"{base_url}-fe.amazon.com", "A1VC38T7YXB528", "us-west-2"),
        AWSRegion.SG: (f"{base_url}-fe.amazon.com", "A19VAU5U5O7RUS", "us-west-2"),
        AWSRegion.US: (f"{base_url}-na.amazon.com", "ATVPDKIKX0DER", "us-east-1"),
        AWSRegion.BR: (f"{base_url}-na.amazon.com", "A2Q3Y263D00KWC", "us-east-1"),
        AWSRegion.CA: (f"{base_url}-na.amazon.com", "A2EUQ1WTGCTBG2", "us-east-1"),
        AWSRegion.MX: (f"{base_url}-na.amazon.com", "A1AM78C64UM0Y8", "us-east-1"),
        AWSRegion.BE: (f"{base_url}-eu.amazon.com", "AMEN7PMS3EDWL", "eu-west-1"),
    }
    marketplaces[AWSRegion.GB] = marketplaces[AWSRegion.UK]
    return marketplaces
