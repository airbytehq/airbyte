# Zoom Migration Guide

## Upgrading to 1.0.0

As of September 8, 2023, Zoom has [deprecated JWT](https://developers.zoom.us/docs/internal-apps/jwt-faq/) authentication and now supports Oauth instead.

To migrate smoothly, please use [Zoom's migration guide](https://developers.zoom.us/docs/internal-apps/jwt-app-migration/) to create a new server-to-server OAuth app and generate the necessary credentials.

When creating the app, ensure you grant it access to the following scopes:

- user:read:admin
- meeting:read:admin
- webinar:read:admin
- chat_channel:read:admin
- report:read:admin

To successfully authenticate your connection in Airbyte, you will need to input the following OAuth credentials:

- client_id
- client_secret
- account_id
- authorization_ednpoint
