# Langchain


## Overview

This destination prepares data to be used by [Langchain](https://langchain.com/) to retrieve relevant context for question answering use cases.

There are three parts to this:
* Processing - split up individual records in chunks so they will fit the context window and decide which fields to use as context and which are supplementary metadata.
* Embedding - convert the text into a vector representation using a pre-trained model (currently only OpenAI `text-embedding-ada-002` is supported)
* Indexing - store the vectors in a vector database for similarity search

### Processing

Each record will be split into text fields and meta fields as configured in the "Processing" section. All text fields are concatenated into a single string and then split into chunks of configured length. The meta fields are stored as-is along with the embedded text chunks. Please note that meta data fields can only be used for filtering and not for retrieval and have to be of type string, number, boolean (all other values are ignored). Depending on the chosen vector store, additional limitations might apply.

When specifying text fields, you can access nested fields in the record by using dot notation, e.g. `user.name` will access the `name` field in the `user` object. It's also possible to use wildcards to access all fields in an object, e.g. `users.*.name` will access all `names` fields in all entries of the `users` array.

The chunk length is measured in tokens produced by the `tiktoken` library. The maximum is 8191 tokens, which is the maximum length supported by the `text-embedding-ada-002` model.

The stream name gets added as a metadata field `_airbyte_stream` to each document. If available, the primary key of the record is used to identify the document to avoid duplications when updated versions of records are indexed. It is added as the `_natural_id` metadata field.

### Embedding

THe OpenAI embedding API is used to calculate embeddings - see [OpenAI API](https://beta.openai.com/docs/api-reference/text-embedding) for details. To do so, an OpenAI API key is required.

This integration will be constrained by the [speed of the OpenAI embedding API](https://platform.openai.com/docs/guides/rate-limits/overview).

For testing purposes, it's also possible to use the [Fake embeddings](https://python.langchain.com/docs/modules/data_connection/text_embedding/integrations/fake) integration. It will generate random embeddings and is suitable to test a data pipeline without incurring embedding costs.

### Indexing

#### DocArrayHnswSearch vector store

For local testing, the [DocArrayHnswSearch](https://python.langchain.com/docs/modules/data_connection/vectorstores/integrations/docarray_hnsw) is recommended - it stores the vectors in a local file with a sqlite database for metadata. It is not suitable for production use, but it is the easiest to set up for testing and development purposes.

The `destination_path` has to start with `/local`. Any directory nesting within local will be mapped onto the local mount.

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

DocArrayHnswSearch does not support incremental sync, so the destination will always do a full refresh sync.

To initialize a langchain QA chain based on the indexed data, use the following code (set the openai API key as `OPENAI_API_KEY` env variable):

```python
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import DocArrayHnswSearch
from langchain.embeddings import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()
vector_store = DocArrayHnswSearch.from_params(embeddings, "/tmp/airbyte_local/<your configured directory>", 1536)

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())
```

:::danger

This destination will delete all existing files in the configured directory on each. Make sure to not use a directory that contains other files.

:::

:::caution

DocArrayHnswSearch is meant to be used on a local workstation and won't work on Kubernetes.

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

#### Pinecone vector store

For production use, use the pinecone vector store. Use the Pinecone web UI or API to create a project and an index before running the destination. All streams will be indexed into the same index, the `_airbyte_stream` metadata field is used to distinguish between streams. Overall, the size of the metadata fields is limited to 30KB per document. Both OpenAI and Fake embeddings are produced with 1536 vector dimensions, make sure to configure the index accordingly.

To initialize a langchain QA chain based on the indexed data, use the following code (set the open API key and pinecone key and environment as `OPENAI_API_KEY`, `PINECONE_KEY` and `PINECONE_ENV` env variables):

```python
from langchain import OpenAI
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings import OpenAIEmbeddings
import pinecone
import os

embeddings = OpenAIEmbeddings()
pinecone.init(api_key=os.environ["PINECONE_KEY"], environment=os.environ["PINECONE_ENV"])
index = pinecone.Index("<your pinecone index name>")
vector_store = Pinecone(index, embeddings.embed_query, "text")

qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=vector_store.as_retriever())
```

## CHANGELOG

| Version | Date       | Pull Request                                                  | Subject                                                                                                                                              |
|:--------| :--------- |:--------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.0.2   | 2023-07-18 | [#26184](https://github.com/airbytehq/airbyte/pull/28398)     | Adjust python dependencies and release on cloud  |
| 0.0.1   | 2023-07-12 | [#26184](https://github.com/airbytehq/airbyte/pull/26184)     | Initial release  |
