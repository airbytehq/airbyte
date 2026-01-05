---
sidebar_label: document_rendering
title: airbyte._util.document_rendering
---

Methods for converting Airbyte records into documents.

## annotations

## TYPE\_CHECKING

## Any

## yaml

## BaseModel

## Document

#### \_to\_title\_case

```python
def _to_title_case(name: str) -> str
```

Convert a string to title case.

Unlike Python&#x27;s built-in `str.title` method, this function doesn&#x27;t lowercase the rest of the
string. This is useful for converting &quot;snake_case&quot; to &quot;Title Case&quot; without negatively affecting
strings that are already in title case or camel case.

## CustomRenderingInstructions Objects

```python
class CustomRenderingInstructions(BaseModel)
```

Instructions for rendering a stream&#x27;s records as documents.

#### title\_property

#### content\_properties

#### frontmatter\_properties

#### metadata\_properties

## DocumentRenderer Objects

```python
class DocumentRenderer(BaseModel)
```

Instructions for rendering a stream&#x27;s records as documents.

#### title\_property

#### content\_properties

#### metadata\_properties

#### render\_metadata

#### render\_document

```python
def render_document(record: dict[str, Any]) -> Document
```

Render a record as a document.

The document will be rendered as a markdown document, with content, frontmatter, and an
optional title. If there are multiple properties to render as content, they will be rendered
beneath H2 section headers. If there is only one property to render as content, it will be
rendered without a section header. If a title property is specified, it will be rendered as
an H1 header at the top of the document.

**Returns**:

  A tuple of (content: str, metadata: dict).

#### render\_documents

```python
def render_documents(records: Iterable[dict[str, Any]]) -> Iterable[Document]
```

Render an iterable of records as documents.

