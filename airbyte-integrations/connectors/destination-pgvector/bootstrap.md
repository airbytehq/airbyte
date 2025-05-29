# PGVector Destination Connector Bootstrap

This destination does three things:
* Split records into chunks and separates metadata from text data
* Embeds text data into an embedding vector
* Stores the metadata and embedding vector in Postgres DB with PGVector extension enabled

The record processing is using the text split components from https://python.langchain.com/docs/modules/data_connection/document_transformers/.