# Robinhood Source

This is the repository for the Robinhood source connector, written in the
declarative low-code YAML framework.

## Overview

The Robinhood source connector syncs data from the Robinhood trading platform.
It uses the Robinhood private API to retrieve account information, positions,
orders, dividends, instruments, and more.

**Note:** Robinhood does not have an official public REST API for equities and
options trading. This connector uses the well-documented private API used by
community libraries such as [robin_stocks](https://robin-stocks.readthedocs.io/)
and [sanko/Robinhood](https://github.com/sanko/Robinhood).

## Authentication

The connector requires a pre-generated Robinhood access token. Because
Robinhood's login flow requires interactive multi-factor authentication (MFA),
the token must be obtained outside of Airbyte using a tool such as
`robin_stocks`:

```python
import robin_stocks.robinhood as rh
login = rh.login('email@example.com', 'password', mfa_code='123456')
print(login['access_token'])
```

The access token expires periodically and must be refreshed.

## Streams

| Stream | Endpoint | Auth Required | Incremental |
|---|---|---|---|
| accounts | `/accounts/` | Yes | No |
| positions | `/positions/` | Yes | No |
| portfolios | `/portfolios/` | Yes | No |
| orders | `/orders/` | Yes | Yes |
| instruments | `/instruments/` | Yes | No |
| dividends | `/dividends/` | Yes | No |
| watchlists | `/watchlists/` | Yes | No |
| options_positions | `/options/positions/` | Yes | No |
| options_orders | `/options/orders/` | Yes | No |

## Development

For information about developing locally, see the
[declarative connector development guide](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview).
