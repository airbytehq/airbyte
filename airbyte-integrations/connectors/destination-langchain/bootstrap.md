# Langchain Destination Connector Bootstrap

This destination does three things:

- Split records into chunks and separates metadata from text data
- Embeds text data into an embedding vector
- Stores the metadata and embedding vector in a vector database

The record processing is using the text split components from https://python.langchain.com/docs/modules/data_connection/document_transformers/.

There are two possible providers for generating embeddings, [OpenAI](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/openai) and [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) for testing purposes.

Embedded documents are stored in a vector database. Currently, [Pinecone](https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/pinecone) and the locally stored [DocArrayHnswSearch](https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/docarray_hnsw) are supported.

For all three components, it's easily possible to add new integrations based on the existing abstractions of the langchain library. In some cases (like the pinecone integration), it's necessary to use the underlying APIs directly to implement more features or improve performance.

## Pinecone integration

The pinecone integration is adding stream and primary key to the vector metadata which allows for deduped incremental and full refreshes. It's using the [official pinecone python client](https://github.com/pinecone-io/pinecone-python-client).

You can use the `test_pinecone.py` file to check whether the pipeline works as expected.

## DocArrayHnswSearch integration

The DocArrayHnswSearch integration is storing the vector metadata in a local file in the local root (`/local` in the container, `/tmp/airbyte_local` on the host). It's not possible to dedupe records, so only full refresh syncs are supported. DocArrayHnswSearch uses hnswlib under the hood, but the integration is fully relying on the langchain abstraction.

## Chroma integration

The Chroma integration is storing the vector metadata in a local file in the local root (`/local` in the container, `/tmp/airbyte_local` on the host), similar to the DocArrayHnswSearch. This is called the "persistent client" mode in Chroma. The integration is mostly using langchains abstraction, but it can also dedupe records and reset streams independently.

You can use the `test_local.py` file to check whether the pipeline works as expected.
