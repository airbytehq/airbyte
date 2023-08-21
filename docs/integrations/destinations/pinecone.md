# Pinecone

## Overview

This destination prepares data to be used by [Pinecone](https://pinecone.io/).

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model (Currently, OpenAI's `text-embedding-ada-002` and Cohere's `embed-english-light-v2.0` are supported.)
* Indexing - store the vectors in a vector database for similarity search

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. If specified, the metadata fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Please note that there's a 40kb limit on the _total_ size of the metadata saved for each entry.

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_airbyte_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_natural_id` metadata field.

### Embedding

The connector can use one of the following embedding methods:

1. OpenAI - using [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) , the connector will produce embeddings using the `text-embedding-ada-002` model. This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

2. Cohere - using the Cohere API, the connector will produce embeddings using the `embed-english-light-v2.0` model. 

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

To get started, use the Pinecone web UI or API to create a project and an index before running the destination. All streams will be indexed into the same index, the `_airbyte_stream` metadata field is used to distinguish between streams. Overall, the size of the metadata fields is limited to 30KB per document. 

OpenAI and Fake embeddings produce vectors with 1536 dimensions, and the Cohere embeddings produce vectors with 1024 dimensions. Make sure to configure the index accordingly.

## CHANGELOG

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.0.1   | 2023-07-12 | [#29442](https://github.com/airbytehq/airbyte/pull/29442)     | Pinecone connector with some embedders  | 
