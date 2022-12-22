# Heap Analytics

[Heap Analytics](https://heap.io) is the only digital insights platform that gives you complete understanding of your customers’ digital journeys, so you can quickly improve conversion, retention, and customer delight.

Every action a user takes is [autocaptured](https://heap.io/platform/capture). See them live, analyze later, or let our [Illuminate](https://heap.io/platform/illuminate) functionality automatically generate insights.

The Destination Connector here helps you load data to Heap, so that you could leverage the powerful analytics tool.

## Prerequisites

- Heap Analytics Account
- App Id, also called Environment Id

## Step 1: Set up Heap Analytics

### Heap Analytics Account

#### If you don't have an Account

[Sign up](https://heapanalytics.com/signup) and create your Heap Analytics Account.

### Understand Projects and Environments in Heap

Your Heap account is structured into a series of projects and environments. **Projects** in Heap can be thought of as blank slates and are completely independent of another. **Environments** are subsets of projects that share definitions (defined events, segments, and reports), but do not share any data. More info can be found from [this doc](https://help.heap.io/data-management/data-management-features/projects-environments/).

## Step 2: Prepare the environment Id

You can get the environment ID from the Heap Analytics dashboard. Choose **Account --> Manage --> Projects**.

## Step 3: Set up the destination connector in Airbyte

1. In the left navigation bar, click **Destinations**. In the top-right corner, click **+ new destination**.
2. On the destination setup page, select **Heap Analytics** from the Destination type dropdown and enter a name for this connector.
3. Fill in the environment Id to the field app_id
4. Pick the right API Type, we will cover more details next.

### API Type Overview

Airbyte will load data to Heap by the [server-side APIs](https://developers.heap.io/reference/server-side-apis-overview). There are 3 API types

- [Track Events](https://developers.heap.io/reference/track-1)
- [Add User Properties](https://developers.heap.io/reference/add-user-properties)
- [Add Account Properties](https://developers.heap.io/reference/add-account-properties)

The destination connector supports all types of schemas of source data. However, each configured catalog, or the connector instance, can load one stream only.
The API type and the configuration determine the output stream. The transformation is run in memory that parses the source data to the schema compatible to the Server-Side API.
Since there are 3 APIs, there are 3 different output schemas.

## Step 4: Configure the transformation for an API Type

### Track Events

Use [this API](https://developers.heap.io/reference/track-1) to send custom events to Heap server-side.

The following is the sample cURL command:

```bash
curl \
  -X POST https://heapanalytics.com/api/track\
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "11",
    "identity": "alice@example.com",
    "event": "Send Transactional Email",
    "timestamp": "2017-03-10T22:21:56+00:00", 
    "properties": {
      "subject": "Welcome to My App!",
      "variation": "A"
    }
  }' 
```

There are 4 properties in the request body.

- identity: An identity, typically corresponding to an existing user.
- event: The name of the server-side event.
- properties: An object with key-value properties you want associated with the event.
- timestamp: (optional), the datetime in ISO8601. e.g. "2017-03-10T22:21:56+00:00". Defaults to the current time if not provided.

For `Add User Properties`, You need to configure the following 4 fields in airbyte.

- Identity Column: The attribute name from the source data populated to identity.
- event_column: The attribute name from the source data populated to event.
- Timestamp Column: The attribute name from the source data populated to timestamp. This field is optional. It will be the current time if not provided.
- Property Columns: The attribute names from the source data populated to object properties. If you want to pick multiple attributes, split the names by comma(`,`). If you want to pick ALL attributes, simply put asterisk(`*`).

Note that, if you want to reference an attribute name in an object or an embedded object. You can the daisy-chained (`.`) connections. Let's use an example to illustrate it.

The data source is a json.

```json
{
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
}
```

If you configure the connector like this:

```json
{
  "property_columns": "blocked,created_at,name",
  "event_column": "identities.connection",
  "identity_column": "email",
  "timestamp_column": "updated_at"
}
```

The final data will be transformed to

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

### Add User Properties

[This API](https://developers.heap.io/reference/add-user-properties) allows you to attach custom properties to any identified users from your servers.

The following is the sample cURL command:

```bash
curl \
  -X POST https://heapanalytics.com/api/add_user_properties\
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "11",
    "identity": "bob@example.com",
    "properties": {
      "age": "25",
      "language": "English",
      "profession": "Scientist",
      "email": "bob2@example2.com"
    }
  }' 
```

There are 2 properties in the request body.

- identity: An identity, typically corresponding to an existing user.
- properties: An object with key-value properties you want associated with the event.

For `Add User Properties`, You need to configure the following 2 fields in airbyte.

- Identity Column: The attribute name from the source data populated to identity.
- property_columns: The attribute names from the source data populated to object properties. If you want to pick multiple attributes, split the names by comma(`,`). If you want to pick ALL attributes, simply put asterisk(`*`).

Note that, if you want to reference an attribute name in an object or an embedded object. You can the daisy-chained (`.`) connections. Let's use an example to illustrate it.

The source data is a json

```json
{
  "blocked": false,
  "created_at": "2022-10-21T04:09:59.328Z",
  "email": "marielle.murazik8@hotmail.com",
  "email_verified": false,
  "family_name": "Gutkowski",
  "given_name": "Alysha",
  "identities": {
    "user_id": "26d8952b-2e1e-4b79-b2aa-e363f062701a",
    "connection": "Username-Password-Authentication",
    "provider": "auth0",
    "isSocial": false
  },
  "name": "Lynn Crooks",
  "nickname": "Noe",
  "updated_at": "2022-10-21T04:09:59.328Z",
  "user_id": "auth0|26d8952b-2e1e-4b79-b2aa-e363f062701a",
}
```

If you configure the connector like this:
```json
{
  "property_columns": "identities_provider,created_at,nickname",
  "identity_column": "user_id"
}
```

The final data will be transformed to

```json
{
  "identity": "auth0|26d8952b-2e1e-4b79-b2aa-e363f062701a",
  "properties": {
    "identities_provider": "auth0",
    "created_at": "2022-10-21T04:09:59.328Z",
    "nickname": "Neo"
  }
}
```

### Add Account Properties

[This API](https://developers.heap.io/reference/add-account-properties) allows you to attach custom account properties to users.

The following is the sample cURL command:

```bash
curl \
  -X POST https://heapanalytics.com/api/add_account_properties\
  -H "Content-Type: application/json" \
  -d '{ 
    "app_id": "123456789", 
    "account_id": "Fake Company",
    "properties": {
      "is_in_good_standing": "true",
      "revenue_potential": "123456",
      "account_hq": "United Kingdom",
      "subscription": "Monthly"
    }
  }'
```

There are 2 properties in the request body.

- account_id: Used for single account updates only. An ID for this account.
- properties: Used for single account updates only. An object with key-value properties you want associated with the account.

For `Add Account Properties`, you need to configure the following 2 fields in airbyte.

- Account ID Column: The attribute name from the source data populated to identity.
- Property Columns: The attribute names from the source data populated to object properties. If you want to pick multiple attributes, split the names by comma(`,`). If you want to pick ALL attributes, simply put asterisk(`*`).

Note that, if you want to reference an attribute name in an object or an embedded object. You can the daisy-chained (`.`) connections. Let's use an example to illustrate it.

The source data is a json

```json
{
  "blocked": false,
  "created_at": "2022-10-21T04:08:53.393Z",
  "email": "nedra14@hotmail.com",
  "email_verified": false,
  "family_name": "Tillman",
  "given_name": "Jacinto",
  "identities": {
    "user_id": "815ff3c3-84fa-4f63-b959-ac2d11efc63c",
    "connection": "Username-Password-Authentication",
    "provider": "auth0",
    "isSocial": false
  },
  "name": "Lola Conn",
  "nickname": "Kenyatta",
  "updated_at": "2022-10-21T04:08:53.393Z",
  "user_id": "auth0|815ff3c3-84fa-4f63-b959-ac2d11efc63c"
}
```

If you configure the connector like this:

```json
{
  "property_columns": "family_name,email_verified,blocked",
  "account_id_column": "identities.user_id"
}
```

The final data will be transformed to

```json
{
  "account_id": "815ff3c3-84fa-4f63-b959-ac2d11efc63c",
  "properties": {
    "family_name": "Tillman",
    "email_verified": false,
    "blocked": false
  }
}
```

### Features & Supported sync modes

| Feature                        | Supported?\(Yes/No\) |
| :----------------------------- | :------------------- |
| Ful-Refresh Overwrite          | Yes                  |
| Ful-Refresh Append             | Yes                  |
| Incremental Append             | Yes                  |
| Incremental Append-Deduplicate | Yes                  |

### Rate Limiting & Performance Considerations
Currently, the API Client for Heap Analytics sends one http request per row of source data. It slows down the performance if you have massive data to load to Heap. There is a bulk API offered under Heap, but it's not implemented in the first version.

Please kindly provide your feedback, I am happy to cache the transformed data in memory and load them to the bulk API.

## Future improvements:

- Implement the [Bulk API](https://developers.heap.io/reference/bulk-track) that loads multiple rows of data to Heap Analytics.

## Changelog

| Version | Date       | Pull Request                                             | Subject                             |
| ------- | ---------- | -------------------------------------------------------- | ----------------------------------- |
| 0.1.0   | 2022-10-26 | [18530](https://github.com/airbytehq/airbyte/pull/18530) | Initial Release                     |
