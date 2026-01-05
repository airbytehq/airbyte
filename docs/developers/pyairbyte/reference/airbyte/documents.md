---
sidebar_label: documents
title: airbyte.documents
---

This module contains the `Documents` class for converting Airbyte records into documents.

Generally you will not create `Documents` objects directly. Instead, you can use one of the
following methods to generate documents from records:

- `Source.get_documents()`: Get an iterable of documents from a source.
- `Dataset.to_documents()`: Get an iterable of documents from a dataset.

## annotations

## TYPE\_CHECKING

## Any

## BaseModel

## Field

#### MAX\_SINGLE\_LINE\_LENGTH

#### AIRBYTE\_DOCUMENT\_RENDERING

#### TITLE\_PROPERTY

#### CONTENT\_PROPS

#### METADATA\_PROPERTIES

## Document Objects

```python
class Document(BaseModel)
```

A PyAirbyte document is a specific projection on top of a record.

Documents have the following structure:
- id (str): A unique string identifier for the document.
- content (str): A string representing the record when rendered as a document.
- metadata (dict[str, Any]): Associated metadata about the document, such as the record&#x27;s IDs
  and/or URLs.

This class is duck-typed to be compatible with LangChain project&#x27;s `Document` class.

#### id

#### content

#### metadata

#### last\_modified

#### \_\_str\_\_

```python
def __str__() -> str
```

Return a string representation of the document.

#### page\_content

```python
@property
def page_content() -> str
```

Return the content of the document.

This is an alias for the `content` property, and is provided for duck-type compatibility
with the LangChain project&#x27;s `Document` class.

#### \_\_all\_\_

