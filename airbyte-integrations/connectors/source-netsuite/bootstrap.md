# Netsuite
The Netsuite REST API allows you to pull any records that live in the user's Netsuite instance.

Netsuite is highly customizable, allowing the addition of custom fields and record types. The REST API provides metadata endpoints that return specs for the entire instance's custom configuration.

Since Netsuite's records all have the same primary key, `id`, and the same cursor, `lastModifiedDate`, the streams, including specs, are not hard coded, but instead dynamically generated based on the metadata.
