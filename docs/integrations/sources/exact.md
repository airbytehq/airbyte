# Exact

Cloud business software for SMEs and their accountants.

## Overview

The sync uses the [Rest API](https://start.exactonline.nl/docs/HlpRestAPIResources.aspx?SourceAction=10). See also
the [Developer Reference](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-gettingstarted).

## Supported Endpoints

Exact groups the available endpoints based on their respective service. This source supports the endpoints listed below.
Note, Exact's Sync and Bulk endpoints are designed for data syncing. These endpoints support bulk pagination of 1000
records. All other services are limited to 60 records per page.

- **Sync**
    - cashflow_payment_terms
    - crm_accounts
    - crm_addresses
    - crm_contacts
    - crm_quotation_headers
    - crm_quotation_lines
    - crm_quotations
    - deleted
    - documents_document_attachments
    - documents_documents
    - financial_gl_accounts
    - financial_gl_classifications
    - financial_transaction_lines
    - hrm_leave_absence_hours_by_day
    - inventory_item_warehouses
    - inventory_serial_batch_numbers
    - inventory_stock_positions
    - inventory_stock_serial_batch_numbers
    - inventory_storage_location_stock_positions
    - logistics_items
    - logistics_purchase_item_prices
    - logistics_sales_item_prices
    - logistics_supplier_item
    - project_project_planning
    - project_project_wbs
    - project_projects
    - project_time_cost_transactions
    - purchase_order_purchase_orders
    - sales_invoice_sales_invoices
    - sales_order_goods_deliveries
    - sales_order_goods_delivery_lines
    - sales_order_sales_order_headers
    - sales_order_sales_order_lines
    - sales_order_sales_orders
    - sales_sales_price_list_volume_discounts
- **CRM**
    - account_classifications
    - account_classification_names

## Features

| Feature           | Supported? |
|:------------------|:-----------|
| Full Refresh Sync | Yes        |
| Incremental       | Yes        |

### Incremental Sync

All endpoints support incremental sync. Regular endpoints use the `Modified` field. Sync endpoints use the `Timestamp`
field. Note, that this `Timestamp` represents a row version and is not related to a natural timestamp.

## Limitations

Extracting multiple divisions is not yet supported

## Authentication

Exact uses OAuth for authentication (including for the API). The API has strict rate limits:

- Access tokens can only be retrieved once every 10 minutes.
- Refresh tokens can only be used once.
    - Upon refresh, a new refresh token is returned which should be used in following refresh.
    - Refresh tokens expire after 30 days. This means, when sync doesn't run for more than 30 days, credentials have to
      be manually updated.

### Retrieving Credentials

1. First create a new app
2. Create initial OAuth token

Documentation can also be found
at [Exact Support](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-oauth-eol-oauth-dev-impleovervw).

#### Create a new app

1. Login at [Exact App Center](https://apps.exactonline.com)
2. Click on `My Apps`
3. Click on `Register an App`
4. Fill in a `Name` of the app (e.g., Airbyte)
5. Fill in a `Redirect URI`, note this must be a valid URI as it's used in OAuth flow
6. Find your `Client ID` and `Client Secret` of the created app

#### Create initial OAuth refresh token

See documentation for this step
at [Exact Knowledge Base](https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Content-oauth-eol-oauth-devstep2)

1. In your browser go to the following URL (after replacing the variables).

   `https://start.exactonline.nl/api/oauth2/auth?client_id=<CLIENT_ID>&redirect_uri=<REDIRECT_URI>&response_type=code`

2. Login with an account
3. Exact redirects to URL as `<REDIRECT_URI>?code=<CODE>`
4. Copy the `code` value
    1. Note, this value is likely URL encoded, it has to be decoded before making the following request (for instance
       using [CyberChef](https://cyberchef.org/#recipe=URL_Decode()))
5. Create initial token, for instance curl:

    ```
    curl -X POST 'https://start.exactonline.nl/api/oauth2/token' \
        --data-urlencode 'grant_type=authorization_code' \
        --data-urlencode 'client_id=<CLIENT_ID>' \
        --data-urlencode 'client_secret=<CLIENT_SECRET>' \
        --data-urlencode 'redirect_uri=<REDIRECT_URI>' \
        --data-urlencode 'code=<CODE>'
    ```

6. Response contains the `access_token` and `refresh_token`
7. Bonus: if `access_token` is expired following curl can be used to refresh the token

    ```
    curl -X POST 'https://start.exactonline.nl/api/oauth2/token' \
        --data-urlencode 'grant_type=refresh_token' \
        --data-urlencode 'refresh_token=<REFERSH_TOKEN>' \
        --data-urlencode 'client_id=<CLIENT_ID>' \
        --data-urlencode 'client_secret=<CLIENT_SECRET>' \
    ```

## Changelog

| Version | Date       | Pull Request                                             | Subject                             |
|---------|------------|----------------------------------------------------------|-------------------------------------|
| 0.1.0   | 2022-12-14 | [20480](https://github.com/airbytehq/airbyte/pull/20480) | New Source: Exact                   | 
| 0.2.0   | 2025-00-00 | nr of pr                                                 | Update of source to airbyte-cdk v.6 |
