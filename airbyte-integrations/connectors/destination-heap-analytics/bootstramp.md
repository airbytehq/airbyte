# Heap Analytics Destination

[Heap](https://heap.io) is a product analytics tool that help you collect and analyze understand customers' behavior data in your web apps or mobile apps.Every single click, swipe, tag, pageview and fill will be tracked. It's also called [Auto Capture](https://heap.io/platform/autocapture)

Other than that, developers can write codes to "manually" track an event -- using a JavaScript SDK or a http request. Today, there is a 3rd way, you can import a large set of data via the open source E(t)L platform -- Airbyte.

## Support any types of data source

Airbyte loads data to heap through the [server-side API](https://developers.heap.io/reference/server-side-apis-overview). As long as the data is transformed correctly, and the output includes all required properties, data will be successfully loaded. The api is always on!

All types of data source are supported, but you have to specify where the required properties are extracted from.

Let's use [track events](https://developers.heap.io/reference/track-1) as an example.
The following sample data is an user fetched [Auth0's API](https://auth0.com/docs/api/management/v2#!/Users/get_users).

```json
[{
  "blocked": false,
  "created_at": "2022-10-21T04:09:54.622Z",
  "email": "evalyn_shields@hotmail.com",
  "email_verified": false,
  "family_name": "Brakus",
  "given_name": "Camden",
  "identities": {
    "user_id": "0a12757f-4b19-4e93-969e-c3a2e98fe82b",
    "connection": "Username-Password-Authentication",
    "provider": "auth0",
    "isSocial": false
  },
  "name": "Jordan Yost",
  "nickname": "Elroy",
  "updated_at": "2022-10-21T04:09:54.622Z",
  "user_id": "auth0|0a12757f-4b19-4e93-969e-c3a2e98fe82b"
}]
```

According to [the track API](https://developers.heap.io/reference/track-1), the following attributes are required in the request body.

- app_id: The id of your project or app
- identity: An identity, typically corresponding to an existing user.
- event: The name of the server-side event.
- properties: An object with key-value properties you want associated with the event.
- timestamp: (optional), the datetime in ISO8601. e.g. "2017-03-10T22:21:56+00:00". Defaults to the current time if not provided.

To transform the data, you need to configure the following 4 fields when you create the connector:

- Identity Column: The attribute name from the source data populated to identity.
- event_column: The attribute name from the source data populated to event.
- Timestamp Column: The attribute name from the source data populated to timestamp. This field is optional. It will be the current time if not provided.
- Property Columns: The attribute names from the source data populated to object properties. If you want to pick multiple attributes, split the names by comma(`,`). If you want to pick ALL attributes, simply put asterisk(`*`).

So, if you want to load the following data:

```json
{
  "identity": "evalyn_shields@hotmail.com",
  "event": "Username-Password-Authentication",
  "timestamp": "2022-10-21T04:09:54.622Z", 
  "properties": {
    "blocked": false,
    "created_at": "2022-10-21T04:09:54.622Z",
    "name": "Jordan Yost"
  }
}
```

Here's how you may configure the connector:

```json
{
  "app_id": "11",
  "base_url": "https://heapanalytics.com",
  "api": {
    "api_type": "track",
    "property_columns": "blocked,created_at,name",
    "event_column": "identities.connection",
    "identity_column": "email",
    "timestamp_column": "updated_at"
  }
}
```

Notice, the event property comes from a property `connection` embedded in an object `identities`, that's why you set `event_column` `identities.connection`. It's called dot notation -- write the name of the object, followed by a dot (.), followed by the name of the property.

Similarly, if you want to load a user or an account, there are other set of required properties. To learn more, please refer to the [ReadMe.md](/docs/integrations/destinations/heap-analytics.md).

## Liminations

Though The destination connector supports a generic schema. There are a few limitations.

### Performance

Heap offers a bulk api that allows you to load multiple rows of data. However, it's not implemented in the first version. So every row is a http post request to Heap, it's not efficient. Please submit your request and we will enhance it for you.

### Only one schema is supported in a connector

Because the configuration of the destination connector includes the details of the transformation, a connector only works for one schema. For example, there are 4 tables in a postgres database -- products, orders, users, logs. If you want to import all tables to heap, you may create 4 different connectors. Each connector includes a transformation setting suitable for the corresponding table schema.

### Unable to join 2 streams

If you understand the section above, you may realize there's no way to merge data from 2 streams. Still the postgres example above, the table `products` contains the details(also called metadata) for a given product id. The table `orders` users product id as a foreign key to reference the table `products`. In a SQL console, You can use an `inner join` to combine these 2 table. However, the destination connector is unable to merge them for you. Instead, you may pre-process the data by creating a view in postgres first, and configure Airbyte to load the view, the view that joins these 2 tables.
