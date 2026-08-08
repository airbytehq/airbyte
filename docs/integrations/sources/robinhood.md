# Robinhood

This page contains the setup guide and reference information for the Robinhood source connector.

## Prerequisites

- A Robinhood account
- A valid Robinhood API access token

## Setup guide

### Step 1: Obtain a Robinhood access token

Robinhood does not provide an official developer portal or UI for generating
API tokens for equities and options data. The API used by this connector is
a private API documented by community projects.

To obtain an access token, you can use the
[robin_stocks](https://robin-stocks.readthedocs.io/) Python library to
authenticate programmatically:

```python
import robin_stocks.robinhood as rh
login = rh.login('your_email@example.com', 'your_password', mfa_code='123456')
print(login['access_token'])
```

Copy the access token for use in the next step.

### Step 2: Set up the Robinhood connector in Airbyte

1. In the Airbyte UI, navigate to **Sources** and select **+ New source**.
2. Search for and select **Robinhood**.
3. Enter a **Name** for the source.
4. Paste your **Access Token**.
5. Optionally set a **Start Date** to limit incremental syncs.
6. Select **Set up source**.

## Supported sync modes

The Robinhood source connector supports the following sync modes:

| Feature | Supported? |
|---|---|
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| SSL connection | Yes |

## Supported streams

| Stream | Sync Mode | Description |
|---|---|---|
| accounts | Full Refresh | Core account info: buying power, cash, margin balances, account type |
| positions | Full Refresh | Current stock positions held in the account |
| portfolios | Full Refresh | Portfolio-level aggregates: equity, market value |
| orders | Incremental | Full order history: buys, sells, status, execution details |
| instruments | Full Refresh | Security metadata: ticker, name, symbol, tradability |
| dividends | Full Refresh | Dividend history: amounts, pay dates, state |
| watchlists | Full Refresh | User's watchlists |
| options_positions | Full Refresh | Current options positions held |
| options_orders | Full Refresh | Options order history |

## Important notes

- **Unofficial API**: Robinhood does not publish an official public REST API
  for equities and options. This connector uses the private API documented by
  community projects. The API may change without notice.
- **Token expiration**: Access tokens expire periodically. You must refresh
  your token when it expires. Syncs will fail with a 401 error when the token
  is no longer valid.
- **Rate limiting**: Robinhood does not publish official rate limits. The
  connector uses exponential backoff to handle rate limiting responses.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2026-04-15 | [76374](https://github.com/airbytehq/airbyte/pull/76374) | Initial release: Accounts, Positions, Portfolios, Orders, Instruments, Dividends, Watchlists, Options Positions, Options Orders |

</details>
