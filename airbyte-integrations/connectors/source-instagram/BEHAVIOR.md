# source-instagram: Unique Behaviors

## 1. Hidden Per-Record API Calls for Carousel Media Children

When syncing media records that have children (carousel posts), the `InstagramMediaChildrenTransformation` makes an additional API call for EACH child media ID during record transformation. A carousel post with 10 slides triggers 10 separate HTTP requests to the `/media` endpoint to fetch detailed information (media_type, media_url, timestamp, etc.) for each child.

**Why this matters:** What appears to be a simple media stream read can silently multiply into many additional API calls proportional to the number of carousel slides across all media records. This directly impacts sync duration and rate limit consumption, and the additional calls are invisible from the manifest configuration.

## 2. Access Token Generation for CAT Tests

The easiest way to generate a new access token for CAT tests is through an Airbyte Cloud connection for the Instagram connector. During the OAuth authentication flow, enable browser developer tools, log in to the Instagram test account from LastPass (`[Source-Instagram] Integration test account`), and monitor requests in the Network tab. Look for the `complete_oauth` POST request — the response body contains the access token you need.

After copying the access token, update the credentials in Google Secret Manager (secret: `SECRET_SOURCE-INSTAGRAM__CREDS`).

**Why this matters:** Instagram access tokens are short-lived and there is no simple CLI or API-only way to refresh them for testing. Without this workflow, engineers waste time trying to figure out how to get a working token for local reads or CAT test runs.
