bit.io Destination
==================
This allows the use of the bit.io service as a destination in Airbyte.

The bit.io destination is a `SpecModifiyingDestination` that hardcodes the host, port, and
ssl options from the `PostgresDestination`.

Testing
-------

To test you need a bit.io user with an empty database. 

Then, create `secrets/credentials.json`

```
{
  "username": "<bit.io username>",
  "database": "<bit.io database name>",
  "connect_password": "<bit.io connect password>"
}
```

Then you can run the standard set of gradle-driven tests. 

NOTE THAT THE DATABASE CONTENTS WILL BE DESTROYED BY TESTS. So don't use a database
with anythign in it. 


