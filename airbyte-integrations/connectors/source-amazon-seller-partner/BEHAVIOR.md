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
