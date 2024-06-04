# Pocket API

Pocket's /v3/get endpoint is a single call that is incredibly versatile. A few examples of the types of requests you can make:

- Retrieve a user’s list of unread items
- Sync data that has changed since the last time your app checked
- Retrieve paged results sorted by the most recent saves
- Retrieve just videos that the user has saved
- Search for a given keyword in item’s title and url
- Retrieve all items for a given domain
- and more

## Required Permissions

In order to use the /v3/get endpoint, your consumer key must have the "Retrieve" permission.

## Secret generation

In order to generate both needed secrets to authenticate (consumer key and access token), you can follow the steps described in [https://docs.airbyte.com/integrations/sources/pocket](https://docs.airbyte.com/integrations/sources/pocket)
