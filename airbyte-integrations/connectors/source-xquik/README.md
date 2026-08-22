# Xquik Source

This directory contains the manifest-only Airbyte source for the [Xquik API](https://docs.xquik.com/api-reference/overview).

The connector replicates public X data through four streams:

- `tweets_search`: Tweets matching one or more advanced search queries.
- `user_profiles`: Public profiles for configured usernames or user IDs.
- `user_tweets`: Public timelines for configured usernames or user IDs.
- `trends`: Regional trends for configured WOEIDs.

See the [Airbyte connector documentation](../../../docs/integrations/sources/xquik.md) for setup and sync behavior.
