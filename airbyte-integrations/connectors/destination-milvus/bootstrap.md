# Milvus Destination Connector Bootstrap

This destination does three things:

- Split records into chunks and separates metadata from text data
- Embeds text data into an embedding vector
- Stores the metadata and embedding vector in a vector database

The record processing is using the text split components from https://python.langchain.com/docs/modules/data_connection/document_transformers/.

There are various possible providers for generating embeddings, delivered as part of the CDK (`airbyte_cdk.destinations.vector_db_based`).

Embedded documents are stored in the Milvus vector database.
