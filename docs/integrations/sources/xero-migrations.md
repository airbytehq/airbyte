# Xero Migration Guide

## Upgrading to 1.0.0

Streams can be accessed only via `access_token`, Follow the documentation - https://developer.xero.com/documentation/guides/oauth2/pkce-flow for understanding more about how to get access token.
As Xero API now only supports date-precision filtering, reads are setting down to full_refresh.
 