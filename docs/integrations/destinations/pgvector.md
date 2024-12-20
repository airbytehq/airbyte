# PGVector Destination

## Overview

This page guides you through the process of setting up the PGVector destination connector.

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model. Currently supported:
  * OpenAI's `text-embedding-ada-002`
  * Cohere's `embed-english-light-v2.0` 
  * Azure OpenAI 
  * Fake `random vectors with 1536 embedding dimensions`
  * OpenAI-compatible
  * Coming soon: Hugging Face's `e5-base-v2`.
* Postgres Connection - where to store the vectors. This configures a vector store using Postgres tables having the `VECTOR` data type which is achieved installing pgvector.

## Prerequisites

To use the PGVector destination, you'll need:

- An account with API access depending on which embedding method you want to use.
- A Postgres DB with support for [pgvector](https://github.com/pgvector/pgvector).

You'll need the following information to configure the destination:

- **Embedding service API Key** - The API key for your embedding account and other params depending on your model.
- **Port** - The port number the server is listening on. Defaults to the PostgreSQL™ standard port
  number (5432).
- **Username**
- **Password**
- **Default Schema Name** - Specify the schema (or several schemas separated by commas) to be set in
  the search-path. These schemas will be used to resolve unqualified object names used in statements
  executed over this connection.
- **Database** - The database name. The default is to connect to a database with the same name as
  the user name.

#### Configure Network Access

Make sure your Postgres database can be accessed by Airbyte. If your database is within a VPC, you
may need to allow access from the IP you're using to expose Airbyte.

## Step 1: Set up Postgres

#### **Permissions**

You need a Postgres user with the following permissions:

- can create tables and write rows.
- can create schemas e.g:

You can create such a user by running:

```
CREATE USER airbyte_user WITH PASSWORD '<password>';
GRANT CREATE, TEMPORARY ON DATABASE <database> TO airbyte_user;
```

You can also use a pre-existing user but we highly recommend creating a dedicated user for Airbyte.

Enable the extension. Here you can find the [official documentation](https://github.com/pgvector/pgvector).
```
CREATE EXTENSION vector;
```
## Step 2: Set up the PGVector connector in Airbyte

#### Target Database

You will need to choose an existing database or create a new database that will be used to store
synced data from Airbyte.

## Naming Conventions

From
[Postgres SQL Identifiers syntax](https://www.postgresql.org/docs/9.0/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS):

- SQL identifiers and key words must begin with a letter \(a-z, but also letters with diacritical
  marks and non-Latin letters\) or an underscore \(\_\).
- Subsequent characters in an identifier or key word can be letters, underscores, digits \(0-9\), or
  dollar signs \($\).

  Note that dollar signs are not allowed in identifiers according to the SQL standard, so their use
  might render applications less portable. The SQL standard will not define a key word that contains
  digits or starts or ends with an underscore, so identifiers of this form are safe against possible
  conflict with future extensions of the standard.

- The system uses no more than NAMEDATALEN-1 bytes of an identifier; longer names can be written in
  commands, but they will be truncated. By default, NAMEDATALEN is 64 so the maximum identifier
  length is 63 bytes
- Quoted identifiers can contain any character, except the character with code zero. \(To include a
  double quote, write two double quotes.\) This allows constructing table or column names that would
  otherwise not be possible, such as ones containing spaces or ampersands. The length limitation
  still applies.
- Quoting an identifier also makes it case-sensitive, whereas unquoted names are always folded to
  lower case.
- In order to make your applications portable and less error-prone, use consistent quoting with each
  name (either always quote it or never quote it).

:::info

Airbyte Postgres destination will create raw tables and schemas using the Unquoted identifiers by
replacing any special characters with an underscore. All final tables and their corresponding
columns are created using Quoted identifiers preserving the case sensitivity. Special characters in final
tables are replaced with underscores.

:::


1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Destinations**. In the top-right corner, click **new
   destination**.
3. On the Set up the destination page, enter the name for the PGVector connector and select
   **Postgres** from the Destination type dropdown.
4. Enter a name for your source.
5. Enter processing information.
6. Enter embedding information.
7. For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your
   Postgres database.
8. Enter the **Default Schemas**.

:::note

The schema names are case sensitive. The 'public' schema is set by default.

:::

7. For **User** and **Password**, enter the username and password you created in
   [Step 1](#step-1-optional-create-a-dedicated-read-only-user).


## Features

| Feature                        | Supported?           | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |

## Data type mapping

All fields specified as metadata fields will be stored in the metadata object of the document and can be used for filtering. The following data types are allowed for metadata fields:
* String
* Number (integer or floating point, gets converted to a 64 bit floating point)
* Booleans (true, false)
* List of String

All other fields are ignored.

## Configuration

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Please note that there's a 40kb limit on the _total_ size of the metadata saved for each entry.  Options around configuring the chunking process use the [Langchain Python library](https://python.langchain.com/docs/get_started/introduction).

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_ab_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_ab_record_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model with **1536 dimensions**. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the [Cohere API](https://docs.cohere.com/reference/embed), the connector will produce embeddings using the `embed-english-light-v2.0` model with **1024 dimensions**.

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing/Data Storage 

- For the **Host**, **Port**, and **DB Name**, enter the hostname, port number, and name for your
   Postgres database.
- List the **Default Schemas**.

All streams will be indexed/stored into a table with the same name. The table will be created if it doesn't exist. The table will have the following columns: 
- document_id (string) - the unique identifier of the document, creating from appending the primary keys in the stream schema
- chunk_id (string) - the unique identifier of the chunk, created by appending the chunk number to the document_id
- metadata (variant) - the metadata of the document, stored as key-value pairs
- document_content (string) - the text content of the chunk
- embedding (vector) - the embedding of the chunk, stored as a list of floats


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.1   | 2024-09-23 | [#45636](https://github.com/airbytehq/airbyte/pull/45636)     | Add default values for default_schema and port.
| 0.1.0   | 2024-09-16 | [#45428](https://github.com/airbytehq/airbyte/pull/45428)     | Add support for PGVector as a Vector destination.

</details>
