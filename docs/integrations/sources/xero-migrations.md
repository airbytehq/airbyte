# Xero Migration Guide

## Upgrading to 1.0.0

The authentication scheme is now using `access_token` instead of Oauth 2.0, Follow the documentation - https://developer.xero.com/documentation/guides/oauth2/pkce-flow for understanding more about how to get access token.
As Xero API now only supports date-precision filtering, reads are streamlined to full_refresh.
