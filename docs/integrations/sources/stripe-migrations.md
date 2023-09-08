# Stripe Migration Guide

## Upgrading to 4.0.0

A major update of most streams to support event-based incremental sync mode. This allows the connector to pull not only the newly created data since the last sync, but the modified data as well.
A schema refresh is required for the connector to use the new cursor format.