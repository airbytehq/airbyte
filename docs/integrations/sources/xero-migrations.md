# Xero Migration Guide

## Upgrading to 1.0.0

The authentication scheme is now using `access_token` instead of Oauth 2.0, Follow the documentation - https://developer.xero.com/documentation/guides/oauth2/pkce-flow for understanding more about how to get access token.
Steps to get access_token via postman:
- Move to Authorization tab of an empty http request and selected Oauth 2.0
- Set use token type as `access token`
- Set header prefix as `Bearer`
- Set grant type as `Authorization code`
- Check `Authorize using browser`
- Set Auth URL as `https://login.xero.com/identity/connect/authorize`
- Set Access token URL as `https://identity.xero.com/connect/token`
- Set Client ID, Client secret, Scope defined as your Xero settings
- Set state as any number Eg: `123`
- Set Client Authentication as `Send as Basic Auth Header`
- Click `Get New Access Token` for retrieving access token

As Xero API now only supports date-precision instead of second precision filtering through If-Modified-Since header, reads are streamlined to incremental through client side.
