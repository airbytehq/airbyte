---
id: airbyte-documents
title: airbyte.documents
---

This module contains the `Documents` class for converting Airbyte records into documents.

Generally you will not create `Documents` objects directly. Instead, you can use one of the
following methods to generate documents from records:

- `Source.get_documents()`: Get an iterable of documents from a source.
- `Dataset.to_documents()`: Get an iterable of documents from a dataset.

### `Document` {#airbyte.documents.Document}

<ApiMember kind="class">

<ApiSignature>

```python
class Document(**data: Any)
```

</ApiSignature>

A PyAirbyte document is a specific projection on top of a record.

Documents have the following structure:
- id (str): A unique string identifier for the document.
- content (str): A string representing the record when rendered as a document.
- metadata (dict[str, Any]): Associated metadata about the document, such as the record's IDs
  and/or URLs.

This class is duck-typed to be compatible with LangChain project's `Document` class.

Raises ``ValidationError`` if the input data cannot be
validated to form a valid model.

`self` is explicitly positional-only to allow `self` as a field name.

#### Attributes {#airbyte.documents.Document--attributes}

- **`content`**&nbsp;(`str`)

- **`id`**&nbsp;(`str | None`)

- **`last_modified`**&nbsp;(`datetime.datetime | None`)

- **`metadata`**&nbsp;(`dict[str, Any]`)

- **`page_content`**&nbsp;(`str`) — Return the content of the document.  This is an alias for the `content` property, and is provided for duck-type compatibility with the LangChain project's `Document` class.

</ApiMember>