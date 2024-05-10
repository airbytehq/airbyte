## Firebase Realtime Database database structure and API specification

Firebase Realtime Database’s database is a JSON tree. The database is specified by URL “https://{database-name}.firebaseio.com/”.
If we have data in the database "https://my-database.firebaseio.com/" as below,

```json
{
  "my-data": {
    "dinosaurs": {
      "lambeosaurus": {
        "height": 2.1,
        "length": 12.5,
        "weight": 5000
      },
      "stegosaurus": {
        "height": 4,
        "length": 9,
        "weight": 2500
      }
    }
  }
}
```

We can fetch "dinosaurs" data by specifying the path `https://my-database.firebaseio.com/my-data/dinosaurs.json".
Then it returns data as follows,

```json
{
  "lambeosaurus": {
    "height": 2.1,
    "length": 12.5,
    "weight": 5000
  },
  "stegosaurus": {
    "height": 4,
    "length": 9,
    "weight": 2500
  }
}
```

This connector emits the records having a "key" column which value is key of JSON object, and a "value" column which value is stringified value of JSON object.
For example, in the above case, it emits records like below.

```json
{"stream": "dinosaurs", "data": {"key": "lambeosaurus", "value": "{\"height\": 2.1,\"length\": 12.5,\"weight\": 5000}"}, "emitted_at": 1640962800000}
{"stream": "dinosaurs", "data": {"key": "stegosaurus", "value": "{\"height\": 4,\"length\": 9,\"weight\": 2500}"}, "emitted_at": 1640962800000}
```

The connector sync only one stream specified by the path user configured. In the above case, if user set database_name="my-database" and path="my-data/dinosaurs", the stream is "dinosaurs" only.

## Authentication

This connector authenticates with a Google Cloud's service-account with the "Firebase Realtime Database Viewer" roles, which grants permissions to read from Firebase Realtime Database.

## Source Acceptance Test specification

We register the test data in the database before executing the source acceptance test. The test data to be registered is `integration_tests/records.json`. We delete all records after test execution. Data registration and deletion are performed via REST API using curl, but since OAuth2 authentication is performed using a Google Cloud's service-account, an access token is obtained using the gcloud command. Therefore, these processes are executed on the `cloudsdktool/google-cloud-cli` container.
