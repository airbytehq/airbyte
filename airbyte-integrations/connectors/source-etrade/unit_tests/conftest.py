#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import pytest
from requests_oauthlib import OAuth1


@pytest.fixture
def auth():
    return OAuth1(
        client_key="test_consumer_key",
        client_secret="test_consumer_secret",
        resource_owner_key="test_oauth_token",
        resource_owner_secret="test_oauth_token_secret",
        signature_method="HMAC-SHA1",
    )


@pytest.fixture
def base_url():
    return "https://apisb.etrade.com"


@pytest.fixture
def config():
    return {
        "consumer_key": "test_consumer_key",
        "consumer_secret": "test_consumer_secret",
        "oauth_token": "test_oauth_token",
        "oauth_token_secret": "test_oauth_token_secret",
        "sandbox": True,
        "account_id_keys": [],
        "start_date": "2024-01-01",
    }


@pytest.fixture
def account_id_keys():
    return ["abc123", "def456"]


MOCK_ACCOUNTS_RESPONSE = {
    "AccountListResponse": {
        "Accounts": {
            "Account": [
                {
                    "accountId": "12345678",
                    "accountIdKey": "abc123",
                    "accountMode": "MARGIN",
                    "accountDesc": "Brokerage Account",
                    "accountName": "Individual Brokerage",
                    "accountType": "INDIVIDUAL",
                    "institutionType": "BROKERAGE",
                    "instNo": 1,
                    "accountStatus": "ACTIVE",
                    "closedDate": 0,
                    "shareWorksAccount": False,
                },
                {
                    "accountId": "87654321",
                    "accountIdKey": "def456",
                    "accountMode": "CASH",
                    "accountDesc": "IRA Account",
                    "accountName": "Traditional IRA",
                    "accountType": "IRA",
                    "institutionType": "BROKERAGE",
                    "instNo": 2,
                    "accountStatus": "ACTIVE",
                    "closedDate": 0,
                    "shareWorksAccount": False,
                },
            ]
        }
    }
}


MOCK_PORTFOLIO_RESPONSE = {
    "PortfolioResponse": {
        "AccountPortfolio": [
            {
                "Position": [
                    {
                        "positionId": 1001,
                        "symbolDescription": "APPLE INC",
                        "pricePaid": 150.0,
                        "quantity": 10.0,
                        "marketValue": 1750.0,
                        "totalCost": 1500.0,
                        "totalGain": 250.0,
                        "totalGainPct": 16.67,
                        "positionType": "LONG",
                        "Product": {
                            "symbol": "AAPL",
                            "securityType": "EQ",
                        },
                    },
                    {
                        "positionId": 1002,
                        "symbolDescription": "MICROSOFT CORP",
                        "pricePaid": 300.0,
                        "quantity": 5.0,
                        "marketValue": 1750.0,
                        "totalCost": 1500.0,
                        "totalGain": 250.0,
                        "totalGainPct": 16.67,
                        "positionType": "LONG",
                        "Product": {
                            "symbol": "MSFT",
                            "securityType": "EQ",
                        },
                    },
                ]
            }
        ],
        "Totals": {
            "totalPages": 1,
            "pageNumber": 0,
        },
    }
}


MOCK_BALANCE_RESPONSE = {
    "BalanceResponse": {
        "accountId": "12345678",
        "accountType": "INDIVIDUAL",
        "optionLevel": "LEVEL_4",
        "accountDescription": "Brokerage Account",
        "accountMode": "MARGIN",
        "Cash": {
            "fundsForOpenOrdersCash": 0.0,
            "moneyMktBalance": 5000.0,
        },
        "Computed": {
            "cashAvailableForInvestment": 10000.0,
            "cashAvailableForWithdrawal": 10000.0,
            "netCash": 10000.0,
            "cashBalance": 10000.0,
            "marginBuyingPower": 20000.0,
            "cashBuyingPower": 10000.0,
            "RealTimeValues": {
                "totalAccountValue": 25000.0,
                "netMv": 15000.0,
                "netMvLong": 15000.0,
                "netMvShort": 0.0,
            },
        },
    }
}


MOCK_TRANSACTIONS_RESPONSE = {
    "TransactionListResponse": {
        "Transaction": [
            {
                "transactionId": 2001,
                "transactionDate": 1704067200000,
                "postDate": 1704153600000,
                "amount": -1500.0,
                "description": "Bought 10 shares of AAPL",
                "transactionType": "BUY",
                "Brokerage": {
                    "transactionType": "BUY",
                    "quantity": 10.0,
                    "price": 150.0,
                    "fee": 0.0,
                    "Product": {
                        "symbol": "AAPL",
                        "securityType": "EQ",
                    },
                },
            },
            {
                "transactionId": 2002,
                "transactionDate": 1704240000000,
                "postDate": 1704326400000,
                "amount": 500.0,
                "description": "Dividend payment",
                "transactionType": "DIVIDEND",
            },
        ],
        "marker": None,
    }
}


MOCK_ORDERS_RESPONSE = {
    "OrdersResponse": {
        "Order": [
            {
                "orderId": 3001,
                "orderPlacedTime": 1704067200000,
                "orderStatus": "EXECUTED",
                "orderType": "EQ",
                "OrderDetail": [
                    {
                        "orderNumber": 3001,
                        "status": "EXECUTED",
                        "orderType": "EQ",
                        "orderTerm": "GOOD_FOR_DAY",
                        "priceType": "MARKET",
                        "Instrument": [
                            {
                                "symbolDescription": "APPLE INC",
                                "orderAction": "BUY",
                                "orderedQuantity": 10.0,
                                "filledQuantity": 10.0,
                                "Product": {
                                    "symbol": "AAPL",
                                    "securityType": "EQ",
                                },
                            }
                        ],
                    }
                ],
            }
        ],
        "marker": None,
    }
}


MOCK_QUOTES_RESPONSE = {
    "QuoteResponse": {
        "QuoteData": [
            {
                "dateTime": "15:30:00 EST 01-01-2024",
                "dateTimeUTC": 1704067200,
                "quoteStatus": "REALTIME",
                "Product": {
                    "symbol": "AAPL",
                    "securityType": "EQ",
                },
                "All": {
                    "ask": 175.50,
                    "bid": 175.40,
                    "lastTrade": 175.45,
                    "high": 176.0,
                    "low": 174.0,
                    "open": 175.0,
                    "totalVolume": 50000000,
                    "companyName": "APPLE INC",
                    "pe": 28.5,
                    "eps": 6.15,
                    "high52": 200.0,
                    "low52": 140.0,
                    "previousClose": 174.0,
                },
            }
        ]
    }
}


MOCK_ALERTS_RESPONSE = {
    "AlertsResponse": {
        "Alert": [
            {
                "id": 4001,
                "createTime": 1704067200000,
                "subject": "AAPL price alert",
                "status": "UNREAD",
                "category": "STOCK",
            },
            {
                "id": 4002,
                "createTime": 1704153600000,
                "subject": "Account deposit received",
                "status": "READ",
                "category": "ACCOUNT",
            },
        ]
    }
}


MOCK_ALERT_DETAILS_RESPONSE = {
    "AlertDetailsResponse": {
        "id": 4001,
        "createTime": 1704067200000,
        "subject": "AAPL price alert",
        "msgText": "AAPL has reached your target price of $175.00",
        "symbol": "AAPL",
    }
}


MOCK_PRODUCT_LOOKUP_RESPONSE = {
    "LookupResponse": {
        "Data": [
            {
                "symbol": "AAPL",
                "description": "APPLE INC COM",
                "type": "EQUITY",
                "exchange": "NMS",
            },
            {
                "symbol": "AMZN",
                "description": "AMAZON COM INC COM",
                "type": "EQUITY",
                "exchange": "NMS",
            },
        ]
    }
}
