---
sidebar_label: name_normalizers
title: airbyte._util.name_normalizers
---

Name normalizer classes.

## annotations

## abc

## functools

## re

## TYPE\_CHECKING

## exc

## NameNormalizerBase Objects

```python
class NameNormalizerBase(abc.ABC)
```

Abstract base class for name normalizers.

#### normalize

```python
@staticmethod
@abc.abstractmethod
def normalize(name: str) -> str
```

Return the normalized name.

#### normalize\_set

```python
@classmethod
def normalize_set(cls, str_iter: Iterable[str]) -> set[str]
```

Converts string iterable to a set of lower case strings.

#### normalize\_list

```python
@classmethod
def normalize_list(cls, str_iter: Iterable[str]) -> list[str]
```

Converts string iterable to a list of lower case strings.

#### check\_matched

```python
@classmethod
def check_matched(cls, name1: str, name2: str) -> bool
```

Return True if the two names match after each is normalized.

#### check\_normalized

```python
@classmethod
def check_normalized(cls, name: str) -> bool
```

Return True if the name is already normalized.

## LowerCaseNormalizer Objects

```python
class LowerCaseNormalizer(NameNormalizerBase)
```

A name normalizer that converts names to lower case.

#### normalize

```python
@staticmethod
@functools.cache
def normalize(name: str) -> str
```

Return the normalized name.

- All non-alphanumeric characters are replaced with underscores.
- Any names that start with a numeric (&quot;1&quot;, &quot;2&quot;, &quot;123&quot;, &quot;1b&quot; etc.) are prefixed
with and underscore (&quot;_1&quot;, &quot;_2&quot;, &quot;_123&quot;, &quot;_1b&quot; etc.)

**Examples**:

  - &quot;Hello World!&quot; -&gt; &quot;hello_world&quot;
  - &quot;Hello, World!&quot; -&gt; &quot;hello__world&quot;
  - &quot;Hello - World&quot; -&gt; &quot;hello___world&quot;
  - &quot;___Hello, World___&quot; -&gt; &quot;___hello__world___&quot;
  - &quot;Average Sales (%)&quot; -&gt; &quot;average_sales____&quot;
  - &quot;Average Sales (#)&quot; -&gt; &quot;average_sales____&quot;
  - &quot;+1&quot; -&gt; &quot;_1&quot;
  - &quot;-1&quot; -&gt; &quot;_1&quot;

#### \_\_all\_\_

