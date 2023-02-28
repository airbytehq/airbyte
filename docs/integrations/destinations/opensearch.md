# OpenSearch

## Sync overview

### Output schema


Opensearch is a Lucene based search engine that's a type of NoSql storage.  
Documents are created in an `index`, similar to a `table`in a relation database.

The output schema matches the input schema of a source.
Each source `stream` becomes a destination `index`.  
For example, in with a relational database source -  
The DB table name is mapped to the destination index.
The DB table columns become fields in the destination document.  
Each row becomes a document in the destination index.

### Data type mapping

[See Opensearch documentation for detailed information about the field types](https://opensearch.org/docs/latest/opensearch/supported-field-types/index/)
This section should contain a table mapping each of the connector's data types to Airbyte types. At the moment, Airbyte uses the same types used by [JSONSchema](https://json-schema.org/understanding-json-schema/reference/index.html). `string`, `date-time`, `object`, `array`, `boolean`, `integer`, and `number` are the most commonly used data types.

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| text | string | [more info](https://opensearch.org/docs/latest/opensearch/supported-field-types/text/)
| date | date-time | [more info](https://opensearch.org/docs/latest/opensearch/supported-field-types/date/)
| object | object | [more info](https://opensearch.org/docs/latest/opensearch/supported-field-types/object/)
| array | array | [more info](https://opensearch.org/docs/latest/opensearch/supported-field-types/object/)
| boolean | boolean | [more info](https://opensearch.org/docs/2.5/opensearch/supported-field-types/boolean/)
| numeric | integer | [more info](https://opensearch.org/docs/latest/opensearch/supported-field-types/numeric/)


### Features

This section should contain a table with the following format:

| Feature | Supported?(Yes/No) | Notes |
| :--- |:-------------------| :--- |
| Full Refresh Sync | yes                |  |
| Incremental Sync | yes                |  |
| Replicate Incremental Deletes | no                 |  |
| SSL connection | yes                |  |
| SSH Tunnel Support | yes                |  |

### Performance considerations

Batch/bulk writes are performed. Large records may impact performance.  
The connector should be enhanced to support variable batch sizes.

## Getting started

### Requirements

* OpenSearch >= 2.X.0
* Configuration
    * Endpoint URL [ex. https://localhost:9200]
    * Username [optional] (basic auth)
    * Password [optional] (basic auth)
    * CA certificate [optional]
    * Api key ID [optional]
    * Api key secret [optional]
* If authentication is used, the user should have permission to create an index if it doesn't exist, and/or be able to `create` documents

### CA certificate
Ca certificate may be fetched from the OpenSearch server from /usr/share/opensearch/config/certs/http_ca.crt
Fetching example from dockerized OpenSearch:
`docker cp os01:/usr/share/opensearch/config/certs/http_ca.crt .` where os01 is a container's name. For more details please visit https://opensearch.org/docs/latest/install-and-configure/install-opensearch/docker/

### Setup guide
Enter the endpoint URL, select authentication method, and whether to use 'upsert' method when indexing new documents.

### Connection via SSH Tunnel

Airbyte has the ability to connect to an OpenSearch instance via an SSH Tunnel.
The reason you might want to do this because it is not possible \(or against security policy\) to connect to your OpenSearch instance directly \(e.g. it does not have a public IP address\).

When using an SSH tunnel, you are configuring Airbyte to connect to an intermediate server \(a.k.a. a bastion sever\) that _does_ have direct access to the OpenSearch instance.
Airbyte connects to the bastion and then asks the bastion to connect directly to the server.

Using this feature requires additional configuration, when creating the source. We will talk through what each piece of configuration means.

1. Configure all fields for the source as you normally would, except `SSH Tunnel Method`.
2. `SSH Tunnel Method` defaults to `No Tunnel` \(meaning a direct connection\). If you want to use an SSH Tunnel choose `SSH Key Authentication` or `Password Authentication`.
    1. Choose `Key Authentication` if you will be using an RSA private key as your secret for establishing the SSH Tunnel \(see below for more information on generating this key\).
    2. Choose `Password Authentication` if you will be using a password as your secret for establishing the SSH Tunnel.
3. `SSH Tunnel Jump Server Host` refers to the intermediate \(bastion\) server that Airbyte will connect to. This should be a hostname or an IP Address.
4. `SSH Connection Port` is the port on the bastion server with which to make the SSH connection. The default port for SSH connections is `22`, so unless you have explicitly changed something, go with the default.
5. `SSH Login Username` is the username that Airbyte should use when connection to the bastion server. This is NOT the TiDB username.
6. If you are using `Password Authentication`, then `SSH Login Username` should be set to the password of the User from the previous step. If you are using `SSH Key Authentication` TiDB password, but the password for the OS-user that Airbyte is using to perform commands on the bastion.
7. If you are using `SSH Key Authentication`, then `SSH Private Key` should be set to the RSA Private Key that you are using to create the SSH connection. This should be the full contents of the key file starting with `-----BEGIN RSA PRIVATE KEY-----` and ending with `-----END RSA PRIVATE KEY-----`.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2023-02-28 | [](https://github.com/airbytehq/airbyte/pull/) | Initial release. |

