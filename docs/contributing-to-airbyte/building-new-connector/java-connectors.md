# Java Connectors

For some connectors we use `java` as many data platforms, sources and destination have very mature java libraries.

Java connectors are fully embedded in the `gradle` build and follow the normal development process \(more details on [developing locally](../developing-locally.md)\).


### Generate the Template
For the JDBC based sources the Code Generator maybe used to create a module's skeleton. 

```bash
$ cd airbyte-integrations/connector-templates/generator # start from repo root
$ ./generate.sh
```

In menu choose the `"Java JDBC Source"`