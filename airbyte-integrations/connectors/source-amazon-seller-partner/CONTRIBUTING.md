# source-amazon-seller-partner: Unique Behaviors

## 1. Report Responses Are Gzip-Compressed CSV, XML, or JSON (Not Standard REST)

Amazon SP API report streams do not return standard JSON REST responses. Instead, reports are fetched as gzip-compressed files that may contain CSV, XML, or JSON data depending on the report type. The connector uses three custom decoders (`GzipCsvDecoder`, `GzipXmlDecoder`, `GzipJsonDecoder`) to handle each format.

For CSV reports, the column headers can be localized per marketplace. For example, seller feedback reports return different column names depending on the seller's marketplace ID, and some marketplaces use different date formats in their CSV output.

**Why this matters:** A single connector handles three fundamentally different response formats behind the scenes. Adding a new report stream requires knowing which format that report uses and selecting the correct decoder. CSV reports may also need marketplace-specific date parsing logic.

## 2. Reactive Token Invalidation on 403 Errors

When Amazon SP API returns a 403 with a message indicating the access token has expired, the connector's custom authenticator (`AmazonSPOauthAuthenticator`) forcibly invalidates the current token by setting its expiry date to the Unix epoch. This is triggered by a custom backoff strategy (`AmazonSellerPartnerWaitTimeFromHeaderBackoffStrategy`) that detects the 403, calls the authenticator's `invalidate_token()` method via a module-level global reference, and then retries the request with a freshly refreshed token.

**Why this matters:** Token invalidation happens through a global module-level variable linking the backoff strategy to the authenticator instance, which is unusual. If this global reference breaks (e.g., due to refactoring), 403 token-expired errors will not trigger token refresh and will instead fail permanently.

## 3. Reciprocal Retry-After Header for Backoff

The custom backoff strategy computes wait time as the reciprocal of the `Retry-After` header value (i.e., `1 / header_value`) instead of using the header value directly. This is because Amazon's `x-amzn-RateLimit-Limit` header returns requests-per-second, not seconds-to-wait.

**Why this matters:** If you see a `Retry-After` value of 0.5, the connector waits 2 seconds (1/0.5), not 0.5 seconds. This inverted interpretation is specific to Amazon's rate limit header semantics and would produce incorrect wait times if applied to other APIs.

## 4. Regression Tests Will Not Run for This Connector

The OAuth token refresh flow fails when running "locally" or via regression tests due to an issue in the CDK's [`abstract_oauth.py` refresh method](https://github.com/airbytehq/airbyte-python-cdk/blob/9ec30dc780ffc44ef132aee7c728bbc23c77afca/airbyte_cdk/sources/streams/http/requests_native_auth/abstract_oauth.py#L195). This is **only** an issue in local/regression test environments, not in Cloud.

**Alternate testing process:**
1. Create a dev image of the connector branch
2. Set up a new source on a Cloud test account using integration test credentials
3. Set up a destination as `dev/null` — verify source setup succeeds and first sync completes
4. Pin customer actor IDs to the dev image and verify that existing customer syncs continue to run without issues

**PRs for this connector should be rolled out via progressive rollouts** while this local testing limitation exists.

**Why this matters:** You cannot rely on regression tests or local runs to validate changes to this connector. The only reliable way to test is through Cloud with a dev image. Skipping the Cloud-based testing process risks shipping broken changes that won't be caught until production.

## 5. Standard Tests Will Not Pass for All Streams

The test `test_basic_read['config' Test Scenario]` fails for `GET_VENDOR_FORECASTING_RETAIL_REPORT` and `GET_VENDOR_FORECASTING_FRESH_REPORT` due to sandbox account permissions:

> `Report type 56300 does not support account ID of type class com.amazon.partner.account.id.MerchantAccountId.`

This error has been returning since at least v4.4.7 of the connector (before these streams were migrated to low-code). This should be resolved once Standard Tests can bypass specific streams — an upcoming update expected in the next few weeks.

## 6. Known Stream Failures in Testing

The following streams have known failures when running against test/sandbox credentials. These are **not** connector bugs — they are limitations of the test account or sandbox environment.

### Permission Errors (403 Forbidden)

| Stream | Failure Reason |
|--------|---------------|
| VendorDirectFulfillmentShipping | `Forbidden. You don't have permission to access this resource.` |
| VendorOrders | `Forbidden. You don't have permission to access this resource.` (repeated 5 times) |
| GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING | `Access to the resource is forbidden` (403 from POST request to SP-API) |
| GET_ORDER_REPORT_DATA_SHIPPING | `Access to the resource is forbidden` (403 from POST request to SP-API) |

### Timeout Errors

| Stream | Failure Reason |
|--------|---------------|
| GET_FBA_STORAGE_FEE_CHARGES_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_LEDGER_DETAIL_VIEW_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_LEDGER_SUMMARY_VIEW_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_AFN_INVENTORY_DATA_BY_COUNTRY | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_INVENTORY_PLANNING_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_FLAT_FILE_ARCHIVED_ORDERS_DATA_BY_ORDER_DATE | `Job timed out for slice 2023-09-01 to 2023-09-30` |
| GET_STRANDED_INVENTORY_UI_DATA | `Job timed out for slice 2023-09-01 to 2023-09-30` |

### Job Failed to Complete

| Stream | Failure Reason |
|--------|---------------|
| GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_FULFILLMENT_REMOVAL_ORDER_DETAIL_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_REIMBURSEMENTS_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_SELLER_FEEDBACK_DATA | `Job failed to start` |
| GET_FBA_SNS_PERFORMANCE_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_SNS_FORECAST_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_MYI_UNSUPPRESSED_INVENTORY_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_PROMOTION_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_FULFILLMENT_CUSTOMER_SHIPMENT_REPLACEMENT_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_FBA_FULFILLMENT_REMOVAL_SHIPMENT_DETAIL_DATA | `Job failed for slice 2023-09-01 to 2023-09-30` |
| GET_VENDOR_FORECASTING_FRESH_REPORT | `Job failed to start` |
| GET_VENDOR_FORECASTING_RETAIL_REPORT | `Job failed to start` |

### Invalid Input

| Stream | Failure Reason |
|--------|---------------|
| GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE | `RequestedFromDate 2023-09-30T00:00:00.000Z is more than 90 days old` (400 InvalidInput) |
