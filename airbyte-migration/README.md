```
docker-compose down
```

```
docker-compose up db server
```

```
curl -H "Content-Type: application/json" -X POST localhost:8001/api/v1/deployment/export --output /tmp/airbyte_archive.tar.gz
```

```
./gradlew :airbyte-migration:build
```

```
./gradlew :airbyte-migration:build
```

figure out why can't find class path + build the docker image
```
airbyte-migration/build/distributions/airbyte-migration-0.10.0-alpha/bin/airbyte-migration
Error: Could not find or load main class io.airbyte.migration.Migrate
Caused by: java.lang.ClassNotFoundException: io.airbyte.migration.Migrate
```

bring everything back down
```
 docker-compose down -v
```

rezip (or move to java)
`tar -cvf blah.tar.gz .`


the structure of the yamls should be different than what the migrate script is currently looking for
```
docker-compose up
```


```
curl -H "Content-Type: application/x-gzip" -X POST localhost:8001/api/v1/deployment/import --data-binary @/Users/charles/code/airbyte/test.tar.gz
```