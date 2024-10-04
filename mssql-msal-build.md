# Custom MSSQL with msal4j build

follow instructions for [build here](https://docs.airbyte.com/contributing-to-airbyte/developing-locally#connector-contributions), some special notes follow.

 * abctl instructions are a bit broken, used `brew` on mac as [here](https://github.com/airbytehq/abctl?tab=readme-ov-file#quickstart)
 * Set up `airbyte-ci` tool: https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#how-to-install
 * updated to version 4.35.6 with `airbyte-ci update --version 4.35.6`

```sh
airbyte-ci connectors --name=source-mssql build --architecture=linux/amd64 \
  && docker image tag airbyte/source-mssql:dev-linux-amd64 vpipkt/source-mssql:dev-linux-amd64 \
  && docker push vpipkt/source-mssql:dev-linux-amd64
```

Okay had to build it on a linux system and in the end i belielve the right combo was:

* abctl running
* build command without the architecture flag
* waiting a long time
* pushing to docker hub 

Then configuring as shown here:

username: 127a8aa3-23bd-41ad-9a4d-6efd874268dd
host: sql-t-nx-s07464-mirage.database.windows.net
port: 1433
db: sqldb-t-nx-s07464-cwarp-eno
SSL encrypted, verify
hostname *.database.windows.net
jdbc param: loginTimeout=10;authentication=ActiveDirectoryServicePrincipal
