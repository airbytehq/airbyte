---
id: airbyte_agent_sdk-connectors-incident_io-types
title: airbyte_agent_sdk.connectors.incident_io.types
---

Module airbyte_agent_sdk.connectors.incident_io.types
=====================================================
Type definitions for incident-io connector.

Classes
-------

<a id="AirbyteSearchParams"></a>

`AirbyteSearchParams(*args, **kwargs)`
:   Parameters for Airbyte cache search operations (generic, use entity-specific query types for better type hints).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `cursor: str`
    :   The type of the None singleton.

    `fields: list[list[str]]`
    :   The type of the None singleton.

    `limit: int`
    :   The type of the None singleton.

    `query: dict[str, typing.Any]`
    :   The type of the None singleton.

<a id="AlertsAndCondition"></a>

`AlertsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.AlertsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsInCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyCondition]`
    :   The type of the None singleton.

<a id="AlertsAnyCondition"></a>

`AlertsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyValueFilter`
    :   The type of the None singleton.

<a id="AlertsAnyValueFilter"></a>

`AlertsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alert_source_id: Any`
    :   ID of the alert source that generated this alert

    `attributes: Any`
    :   Structured alert attributes

    `created_at: Any`
    :   When the alert was created

    `deduplication_key: Any`
    :   Deduplication key uniquely referencing this alert

    `description: Any`
    :   Description of the alert

    `id: Any`
    :   Unique identifier for the alert

    `resolved_at: Any`
    :   When the alert was resolved

    `source_url: Any`
    :   Link to the alert in the upstream system

    `status: Any`
    :   Status of the alert: firing or resolved

    `title: Any`
    :   Title of the alert

    `updated_at: Any`
    :   When the alert was last updated

<a id="AlertsContainsCondition"></a>

`AlertsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyValueFilter`
    :   The type of the None singleton.

<a id="AlertsEqCondition"></a>

`AlertsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsFuzzyCondition"></a>

`AlertsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.AlertsStringFilter`
    :   The type of the None singleton.

<a id="AlertsGetParams"></a>

`AlertsGetParams(*args, **kwargs)`
:   Parameters for alerts.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="AlertsGtCondition"></a>

`AlertsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsGteCondition"></a>

`AlertsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsInCondition"></a>

`AlertsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.AlertsInFilter`
    :   The type of the None singleton.

<a id="AlertsInFilter"></a>

`AlertsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alert_source_id: list[str]`
    :   ID of the alert source that generated this alert

    `attributes: list[list[typing.Any]]`
    :   Structured alert attributes

    `created_at: list[str]`
    :   When the alert was created

    `deduplication_key: list[str]`
    :   Deduplication key uniquely referencing this alert

    `description: list[str]`
    :   Description of the alert

    `id: list[str]`
    :   Unique identifier for the alert

    `resolved_at: list[str]`
    :   When the alert was resolved

    `source_url: list[str]`
    :   Link to the alert in the upstream system

    `status: list[str]`
    :   Status of the alert: firing or resolved

    `title: list[str]`
    :   Title of the alert

    `updated_at: list[str]`
    :   When the alert was last updated

<a id="AlertsKeywordCondition"></a>

`AlertsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.AlertsStringFilter`
    :   The type of the None singleton.

<a id="AlertsLikeCondition"></a>

`AlertsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.AlertsStringFilter`
    :   The type of the None singleton.

<a id="AlertsListParams"></a>

`AlertsListParams(*args, **kwargs)`
:   Parameters for alerts.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="AlertsLtCondition"></a>

`AlertsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsLteCondition"></a>

`AlertsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsNeqCondition"></a>

`AlertsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.AlertsSearchFilter`
    :   The type of the None singleton.

<a id="AlertsNotCondition"></a>

`AlertsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.AlertsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsInCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyCondition`
    :   The type of the None singleton.

<a id="AlertsOrCondition"></a>

`AlertsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.AlertsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsInCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyCondition]`
    :   The type of the None singleton.

<a id="AlertsSearchFilter"></a>

`AlertsSearchFilter(*args, **kwargs)`
:   Available fields for filtering alerts search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alert_source_id: str | None`
    :   ID of the alert source that generated this alert

    `attributes: list[typing.Any] | None`
    :   Structured alert attributes

    `created_at: str | None`
    :   When the alert was created

    `deduplication_key: str | None`
    :   Deduplication key uniquely referencing this alert

    `description: str | None`
    :   Description of the alert

    `id: str | None`
    :   Unique identifier for the alert

    `resolved_at: str | None`
    :   When the alert was resolved

    `source_url: str | None`
    :   Link to the alert in the upstream system

    `status: str | None`
    :   Status of the alert: firing or resolved

    `title: str | None`
    :   Title of the alert

    `updated_at: str | None`
    :   When the alert was last updated

<a id="AlertsSearchQuery"></a>

`AlertsSearchQuery(*args, **kwargs)`
:   Search query for alerts entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.AlertsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsInCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.AlertsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.AlertsSortFilter]`
    :   The type of the None singleton.

<a id="AlertsSortFilter"></a>

`AlertsSortFilter(*args, **kwargs)`
:   Available fields for sorting alerts search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alert_source_id: Literal['asc', 'desc']`
    :   ID of the alert source that generated this alert

    `attributes: Literal['asc', 'desc']`
    :   Structured alert attributes

    `created_at: Literal['asc', 'desc']`
    :   When the alert was created

    `deduplication_key: Literal['asc', 'desc']`
    :   Deduplication key uniquely referencing this alert

    `description: Literal['asc', 'desc']`
    :   Description of the alert

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the alert

    `resolved_at: Literal['asc', 'desc']`
    :   When the alert was resolved

    `source_url: Literal['asc', 'desc']`
    :   Link to the alert in the upstream system

    `status: Literal['asc', 'desc']`
    :   Status of the alert: firing or resolved

    `title: Literal['asc', 'desc']`
    :   Title of the alert

    `updated_at: Literal['asc', 'desc']`
    :   When the alert was last updated

<a id="AlertsStringFilter"></a>

`AlertsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `alert_source_id: str`
    :   ID of the alert source that generated this alert

    `attributes: str`
    :   Structured alert attributes

    `created_at: str`
    :   When the alert was created

    `deduplication_key: str`
    :   Deduplication key uniquely referencing this alert

    `description: str`
    :   Description of the alert

    `id: str`
    :   Unique identifier for the alert

    `resolved_at: str`
    :   When the alert was resolved

    `source_url: str`
    :   Link to the alert in the upstream system

    `status: str`
    :   Status of the alert: firing or resolved

    `title: str`
    :   Title of the alert

    `updated_at: str`
    :   When the alert was last updated

<a id="CatalogTypesAndCondition"></a>

`CatalogTypesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesInCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyCondition]`
    :   The type of the None singleton.

<a id="CatalogTypesAnyCondition"></a>

`CatalogTypesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyValueFilter`
    :   The type of the None singleton.

<a id="CatalogTypesAnyValueFilter"></a>

`CatalogTypesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Any`
    :   Annotations metadata

    `categories: Any`
    :   Categories this type belongs to

    `color: Any`
    :   Display color

    `created_at: Any`
    :   When the catalog type was created

    `description: Any`
    :   Description of the catalog type

    `icon: Any`
    :   Display icon

    `id: Any`
    :   Unique identifier for the catalog type

    `is_editable: Any`
    :   Whether entries can be edited

    `last_synced_at: Any`
    :   When the catalog type was last synced

    `name: Any`
    :   Name of the catalog type

    `ranked: Any`
    :   Whether entries are ranked

    `registry_type: Any`
    :   Registry type if synced from an integration

    `required_integrations: Any`
    :   Integrations required for this type

    `schema_: Any`
    :   Schema definition for the catalog type

    `semantic_type: Any`
    :   Semantic type for special behavior

    `type_name: Any`
    :   Programmatic type name

    `updated_at: Any`
    :   When the catalog type was last updated

<a id="CatalogTypesContainsCondition"></a>

`CatalogTypesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyValueFilter`
    :   The type of the None singleton.

<a id="CatalogTypesEqCondition"></a>

`CatalogTypesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesFuzzyCondition"></a>

`CatalogTypesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesStringFilter`
    :   The type of the None singleton.

<a id="CatalogTypesGetParams"></a>

`CatalogTypesGetParams(*args, **kwargs)`
:   Parameters for catalog_types.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CatalogTypesGtCondition"></a>

`CatalogTypesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesGteCondition"></a>

`CatalogTypesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesInCondition"></a>

`CatalogTypesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesInFilter`
    :   The type of the None singleton.

<a id="CatalogTypesInFilter"></a>

`CatalogTypesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: list[dict[str, typing.Any]]`
    :   Annotations metadata

    `categories: list[list[typing.Any]]`
    :   Categories this type belongs to

    `color: list[str]`
    :   Display color

    `created_at: list[str]`
    :   When the catalog type was created

    `description: list[str]`
    :   Description of the catalog type

    `icon: list[str]`
    :   Display icon

    `id: list[str]`
    :   Unique identifier for the catalog type

    `is_editable: list[bool]`
    :   Whether entries can be edited

    `last_synced_at: list[str]`
    :   When the catalog type was last synced

    `name: list[str]`
    :   Name of the catalog type

    `ranked: list[bool]`
    :   Whether entries are ranked

    `registry_type: list[str]`
    :   Registry type if synced from an integration

    `required_integrations: list[list[typing.Any]]`
    :   Integrations required for this type

    `schema_: list[dict[str, typing.Any]]`
    :   Schema definition for the catalog type

    `semantic_type: list[str]`
    :   Semantic type for special behavior

    `type_name: list[str]`
    :   Programmatic type name

    `updated_at: list[str]`
    :   When the catalog type was last updated

<a id="CatalogTypesKeywordCondition"></a>

`CatalogTypesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesStringFilter`
    :   The type of the None singleton.

<a id="CatalogTypesLikeCondition"></a>

`CatalogTypesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesStringFilter`
    :   The type of the None singleton.

<a id="CatalogTypesListParams"></a>

`CatalogTypesListParams(*args, **kwargs)`
:   Parameters for catalog_types.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CatalogTypesLtCondition"></a>

`CatalogTypesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesLteCondition"></a>

`CatalogTypesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesNeqCondition"></a>

`CatalogTypesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSearchFilter`
    :   The type of the None singleton.

<a id="CatalogTypesNotCondition"></a>

`CatalogTypesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesInCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyCondition`
    :   The type of the None singleton.

<a id="CatalogTypesOrCondition"></a>

`CatalogTypesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesInCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyCondition]`
    :   The type of the None singleton.

<a id="CatalogTypesSearchFilter"></a>

`CatalogTypesSearchFilter(*args, **kwargs)`
:   Available fields for filtering catalog_types search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `categories: list[typing.Any] | None`
    :   Categories this type belongs to

    `color: str | None`
    :   Display color

    `created_at: str | None`
    :   When the catalog type was created

    `description: str | None`
    :   Description of the catalog type

    `icon: str | None`
    :   Display icon

    `id: str | None`
    :   Unique identifier for the catalog type

    `is_editable: bool | None`
    :   Whether entries can be edited

    `last_synced_at: str | None`
    :   When the catalog type was last synced

    `name: str | None`
    :   Name of the catalog type

    `ranked: bool | None`
    :   Whether entries are ranked

    `registry_type: str | None`
    :   Registry type if synced from an integration

    `required_integrations: list[typing.Any] | None`
    :   Integrations required for this type

    `schema_: dict[str, typing.Any] | None`
    :   Schema definition for the catalog type

    `semantic_type: str | None`
    :   Semantic type for special behavior

    `type_name: str | None`
    :   Programmatic type name

    `updated_at: str | None`
    :   When the catalog type was last updated

<a id="CatalogTypesSearchQuery"></a>

`CatalogTypesSearchQuery(*args, **kwargs)`
:   Search query for catalog_types entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesInCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.CatalogTypesSortFilter]`
    :   The type of the None singleton.

<a id="CatalogTypesSortFilter"></a>

`CatalogTypesSortFilter(*args, **kwargs)`
:   Available fields for sorting catalog_types search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Literal['asc', 'desc']`
    :   Annotations metadata

    `categories: Literal['asc', 'desc']`
    :   Categories this type belongs to

    `color: Literal['asc', 'desc']`
    :   Display color

    `created_at: Literal['asc', 'desc']`
    :   When the catalog type was created

    `description: Literal['asc', 'desc']`
    :   Description of the catalog type

    `icon: Literal['asc', 'desc']`
    :   Display icon

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the catalog type

    `is_editable: Literal['asc', 'desc']`
    :   Whether entries can be edited

    `last_synced_at: Literal['asc', 'desc']`
    :   When the catalog type was last synced

    `name: Literal['asc', 'desc']`
    :   Name of the catalog type

    `ranked: Literal['asc', 'desc']`
    :   Whether entries are ranked

    `registry_type: Literal['asc', 'desc']`
    :   Registry type if synced from an integration

    `required_integrations: Literal['asc', 'desc']`
    :   Integrations required for this type

    `schema_: Literal['asc', 'desc']`
    :   Schema definition for the catalog type

    `semantic_type: Literal['asc', 'desc']`
    :   Semantic type for special behavior

    `type_name: Literal['asc', 'desc']`
    :   Programmatic type name

    `updated_at: Literal['asc', 'desc']`
    :   When the catalog type was last updated

<a id="CatalogTypesStringFilter"></a>

`CatalogTypesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: str`
    :   Annotations metadata

    `categories: str`
    :   Categories this type belongs to

    `color: str`
    :   Display color

    `created_at: str`
    :   When the catalog type was created

    `description: str`
    :   Description of the catalog type

    `icon: str`
    :   Display icon

    `id: str`
    :   Unique identifier for the catalog type

    `is_editable: str`
    :   Whether entries can be edited

    `last_synced_at: str`
    :   When the catalog type was last synced

    `name: str`
    :   Name of the catalog type

    `ranked: str`
    :   Whether entries are ranked

    `registry_type: str`
    :   Registry type if synced from an integration

    `required_integrations: str`
    :   Integrations required for this type

    `schema_: str`
    :   Schema definition for the catalog type

    `semantic_type: str`
    :   Semantic type for special behavior

    `type_name: str`
    :   Programmatic type name

    `updated_at: str`
    :   When the catalog type was last updated

<a id="CustomFieldsAndCondition"></a>

`CustomFieldsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomFieldsAnyCondition"></a>

`CustomFieldsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomFieldsAnyValueFilter"></a>

`CustomFieldsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the custom field was created

    `description: Any`
    :   Description of the custom field

    `field_type: Any`
    :   Type of field

    `id: Any`
    :   Unique identifier for the custom field

    `name: Any`
    :   Name of the custom field

    `updated_at: Any`
    :   When the custom field was last updated

<a id="CustomFieldsContainsCondition"></a>

`CustomFieldsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyValueFilter`
    :   The type of the None singleton.

<a id="CustomFieldsEqCondition"></a>

`CustomFieldsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsFuzzyCondition"></a>

`CustomFieldsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsGetParams"></a>

`CustomFieldsGetParams(*args, **kwargs)`
:   Parameters for custom_fields.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="CustomFieldsGtCondition"></a>

`CustomFieldsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsGteCondition"></a>

`CustomFieldsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsInCondition"></a>

`CustomFieldsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsInFilter`
    :   The type of the None singleton.

<a id="CustomFieldsInFilter"></a>

`CustomFieldsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the custom field was created

    `description: list[str]`
    :   Description of the custom field

    `field_type: list[str]`
    :   Type of field

    `id: list[str]`
    :   Unique identifier for the custom field

    `name: list[str]`
    :   Name of the custom field

    `updated_at: list[str]`
    :   When the custom field was last updated

<a id="CustomFieldsKeywordCondition"></a>

`CustomFieldsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsLikeCondition"></a>

`CustomFieldsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsStringFilter`
    :   The type of the None singleton.

<a id="CustomFieldsListParams"></a>

`CustomFieldsListParams(*args, **kwargs)`
:   Parameters for custom_fields.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="CustomFieldsLtCondition"></a>

`CustomFieldsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsLteCondition"></a>

`CustomFieldsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsNeqCondition"></a>

`CustomFieldsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSearchFilter`
    :   The type of the None singleton.

<a id="CustomFieldsNotCondition"></a>

`CustomFieldsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyCondition`
    :   The type of the None singleton.

<a id="CustomFieldsOrCondition"></a>

`CustomFieldsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyCondition]`
    :   The type of the None singleton.

<a id="CustomFieldsSearchFilter"></a>

`CustomFieldsSearchFilter(*args, **kwargs)`
:   Available fields for filtering custom_fields search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the custom field was created

    `description: str | None`
    :   Description of the custom field

    `field_type: str | None`
    :   Type of field

    `id: str | None`
    :   Unique identifier for the custom field

    `name: str | None`
    :   Name of the custom field

    `updated_at: str | None`
    :   When the custom field was last updated

<a id="CustomFieldsSearchQuery"></a>

`CustomFieldsSearchQuery(*args, **kwargs)`
:   Search query for custom_fields entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsInCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.CustomFieldsSortFilter]`
    :   The type of the None singleton.

<a id="CustomFieldsSortFilter"></a>

`CustomFieldsSortFilter(*args, **kwargs)`
:   Available fields for sorting custom_fields search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the custom field was created

    `description: Literal['asc', 'desc']`
    :   Description of the custom field

    `field_type: Literal['asc', 'desc']`
    :   Type of field

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the custom field

    `name: Literal['asc', 'desc']`
    :   Name of the custom field

    `updated_at: Literal['asc', 'desc']`
    :   When the custom field was last updated

<a id="CustomFieldsStringFilter"></a>

`CustomFieldsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the custom field was created

    `description: str`
    :   Description of the custom field

    `field_type: str`
    :   Type of field

    `id: str`
    :   Unique identifier for the custom field

    `name: str`
    :   Name of the custom field

    `updated_at: str`
    :   When the custom field was last updated

<a id="EscalationsAndCondition"></a>

`EscalationsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.EscalationsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsInCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyCondition]`
    :   The type of the None singleton.

<a id="EscalationsAnyCondition"></a>

`EscalationsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyValueFilter`
    :   The type of the None singleton.

<a id="EscalationsAnyValueFilter"></a>

`EscalationsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the escalation was created

    `creator: Any`
    :   The creator of this escalation

    `escalation_path_id: Any`
    :   ID of the escalation path used

    `events: Any`
    :   History of escalation events

    `id: Any`
    :   Unique identifier for the escalation

    `priority: Any`
    :   Priority of the escalation

    `related_alerts: Any`
    :   Alerts related to this escalation

    `related_incidents: Any`
    :   Incidents related to this escalation

    `status: Any`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: Any`
    :   Title of the escalation

    `updated_at: Any`
    :   When the escalation was last updated

<a id="EscalationsContainsCondition"></a>

`EscalationsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyValueFilter`
    :   The type of the None singleton.

<a id="EscalationsEqCondition"></a>

`EscalationsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsFuzzyCondition"></a>

`EscalationsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.EscalationsStringFilter`
    :   The type of the None singleton.

<a id="EscalationsGetParams"></a>

`EscalationsGetParams(*args, **kwargs)`
:   Parameters for escalations.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="EscalationsGtCondition"></a>

`EscalationsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsGteCondition"></a>

`EscalationsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsInCondition"></a>

`EscalationsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.EscalationsInFilter`
    :   The type of the None singleton.

<a id="EscalationsInFilter"></a>

`EscalationsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the escalation was created

    `creator: list[dict[str, typing.Any]]`
    :   The creator of this escalation

    `escalation_path_id: list[str]`
    :   ID of the escalation path used

    `events: list[list[typing.Any]]`
    :   History of escalation events

    `id: list[str]`
    :   Unique identifier for the escalation

    `priority: list[dict[str, typing.Any]]`
    :   Priority of the escalation

    `related_alerts: list[list[typing.Any]]`
    :   Alerts related to this escalation

    `related_incidents: list[list[typing.Any]]`
    :   Incidents related to this escalation

    `status: list[str]`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: list[str]`
    :   Title of the escalation

    `updated_at: list[str]`
    :   When the escalation was last updated

<a id="EscalationsKeywordCondition"></a>

`EscalationsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.EscalationsStringFilter`
    :   The type of the None singleton.

<a id="EscalationsLikeCondition"></a>

`EscalationsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.EscalationsStringFilter`
    :   The type of the None singleton.

<a id="EscalationsListParams"></a>

`EscalationsListParams(*args, **kwargs)`
:   Parameters for escalations.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="EscalationsLtCondition"></a>

`EscalationsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsLteCondition"></a>

`EscalationsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsNeqCondition"></a>

`EscalationsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.EscalationsSearchFilter`
    :   The type of the None singleton.

<a id="EscalationsNotCondition"></a>

`EscalationsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.EscalationsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsInCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyCondition`
    :   The type of the None singleton.

<a id="EscalationsOrCondition"></a>

`EscalationsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.EscalationsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsInCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyCondition]`
    :   The type of the None singleton.

<a id="EscalationsSearchFilter"></a>

`EscalationsSearchFilter(*args, **kwargs)`
:   Available fields for filtering escalations search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the escalation was created

    `creator: dict[str, typing.Any] | None`
    :   The creator of this escalation

    `escalation_path_id: str | None`
    :   ID of the escalation path used

    `events: list[typing.Any] | None`
    :   History of escalation events

    `id: str | None`
    :   Unique identifier for the escalation

    `priority: dict[str, typing.Any] | None`
    :   Priority of the escalation

    `related_alerts: list[typing.Any] | None`
    :   Alerts related to this escalation

    `related_incidents: list[typing.Any] | None`
    :   Incidents related to this escalation

    `status: str | None`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: str | None`
    :   Title of the escalation

    `updated_at: str | None`
    :   When the escalation was last updated

<a id="EscalationsSearchQuery"></a>

`EscalationsSearchQuery(*args, **kwargs)`
:   Search query for escalations entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.EscalationsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsInCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.EscalationsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.EscalationsSortFilter]`
    :   The type of the None singleton.

<a id="EscalationsSortFilter"></a>

`EscalationsSortFilter(*args, **kwargs)`
:   Available fields for sorting escalations search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the escalation was created

    `creator: Literal['asc', 'desc']`
    :   The creator of this escalation

    `escalation_path_id: Literal['asc', 'desc']`
    :   ID of the escalation path used

    `events: Literal['asc', 'desc']`
    :   History of escalation events

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the escalation

    `priority: Literal['asc', 'desc']`
    :   Priority of the escalation

    `related_alerts: Literal['asc', 'desc']`
    :   Alerts related to this escalation

    `related_incidents: Literal['asc', 'desc']`
    :   Incidents related to this escalation

    `status: Literal['asc', 'desc']`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: Literal['asc', 'desc']`
    :   Title of the escalation

    `updated_at: Literal['asc', 'desc']`
    :   When the escalation was last updated

<a id="EscalationsStringFilter"></a>

`EscalationsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the escalation was created

    `creator: str`
    :   The creator of this escalation

    `escalation_path_id: str`
    :   ID of the escalation path used

    `events: str`
    :   History of escalation events

    `id: str`
    :   Unique identifier for the escalation

    `priority: str`
    :   Priority of the escalation

    `related_alerts: str`
    :   Alerts related to this escalation

    `related_incidents: str`
    :   Incidents related to this escalation

    `status: str`
    :   Status: pending, triggered, acked, resolved, expired, cancelled

    `title: str`
    :   Title of the escalation

    `updated_at: str`
    :   When the escalation was last updated

<a id="IncidentRolesAndCondition"></a>

`IncidentRolesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentRolesAnyCondition"></a>

`IncidentRolesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentRolesAnyValueFilter"></a>

`IncidentRolesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the role was created

    `description: Any`
    :   Description of the role

    `id: Any`
    :   Unique identifier for the incident role

    `instructions: Any`
    :   Instructions for the role holder

    `name: Any`
    :   Name of the role

    `required: Any`
    :   Whether this role must be assigned

    `role_type: Any`
    :   Type of role

    `shortform: Any`
    :   Short form label for the role

    `updated_at: Any`
    :   When the role was last updated

<a id="IncidentRolesContainsCondition"></a>

`IncidentRolesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentRolesEqCondition"></a>

`IncidentRolesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesFuzzyCondition"></a>

`IncidentRolesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesStringFilter`
    :   The type of the None singleton.

<a id="IncidentRolesGetParams"></a>

`IncidentRolesGetParams(*args, **kwargs)`
:   Parameters for incident_roles.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IncidentRolesGtCondition"></a>

`IncidentRolesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesGteCondition"></a>

`IncidentRolesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesInCondition"></a>

`IncidentRolesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesInFilter`
    :   The type of the None singleton.

<a id="IncidentRolesInFilter"></a>

`IncidentRolesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the role was created

    `description: list[str]`
    :   Description of the role

    `id: list[str]`
    :   Unique identifier for the incident role

    `instructions: list[str]`
    :   Instructions for the role holder

    `name: list[str]`
    :   Name of the role

    `required: list[bool]`
    :   Whether this role must be assigned

    `role_type: list[str]`
    :   Type of role

    `shortform: list[str]`
    :   Short form label for the role

    `updated_at: list[str]`
    :   When the role was last updated

<a id="IncidentRolesKeywordCondition"></a>

`IncidentRolesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesStringFilter`
    :   The type of the None singleton.

<a id="IncidentRolesLikeCondition"></a>

`IncidentRolesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesStringFilter`
    :   The type of the None singleton.

<a id="IncidentRolesListParams"></a>

`IncidentRolesListParams(*args, **kwargs)`
:   Parameters for incident_roles.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IncidentRolesLtCondition"></a>

`IncidentRolesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesLteCondition"></a>

`IncidentRolesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesNeqCondition"></a>

`IncidentRolesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentRolesNotCondition"></a>

`IncidentRolesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyCondition`
    :   The type of the None singleton.

<a id="IncidentRolesOrCondition"></a>

`IncidentRolesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentRolesSearchFilter"></a>

`IncidentRolesSearchFilter(*args, **kwargs)`
:   Available fields for filtering incident_roles search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the role was created

    `description: str | None`
    :   Description of the role

    `id: str | None`
    :   Unique identifier for the incident role

    `instructions: str | None`
    :   Instructions for the role holder

    `name: str | None`
    :   Name of the role

    `required: bool | None`
    :   Whether this role must be assigned

    `role_type: str | None`
    :   Type of role

    `shortform: str | None`
    :   Short form label for the role

    `updated_at: str | None`
    :   When the role was last updated

<a id="IncidentRolesSearchQuery"></a>

`IncidentRolesSearchQuery(*args, **kwargs)`
:   Search query for incident_roles entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentRolesSortFilter]`
    :   The type of the None singleton.

<a id="IncidentRolesSortFilter"></a>

`IncidentRolesSortFilter(*args, **kwargs)`
:   Available fields for sorting incident_roles search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the role was created

    `description: Literal['asc', 'desc']`
    :   Description of the role

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the incident role

    `instructions: Literal['asc', 'desc']`
    :   Instructions for the role holder

    `name: Literal['asc', 'desc']`
    :   Name of the role

    `required: Literal['asc', 'desc']`
    :   Whether this role must be assigned

    `role_type: Literal['asc', 'desc']`
    :   Type of role

    `shortform: Literal['asc', 'desc']`
    :   Short form label for the role

    `updated_at: Literal['asc', 'desc']`
    :   When the role was last updated

<a id="IncidentRolesStringFilter"></a>

`IncidentRolesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the role was created

    `description: str`
    :   Description of the role

    `id: str`
    :   Unique identifier for the incident role

    `instructions: str`
    :   Instructions for the role holder

    `name: str`
    :   Name of the role

    `required: str`
    :   Whether this role must be assigned

    `role_type: str`
    :   Type of role

    `shortform: str`
    :   Short form label for the role

    `updated_at: str`
    :   When the role was last updated

<a id="IncidentStatusesAndCondition"></a>

`IncidentStatusesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentStatusesAnyCondition"></a>

`IncidentStatusesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesAnyValueFilter"></a>

`IncidentStatusesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: Any`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: Any`
    :   When the status was created

    `description: Any`
    :   Description of the status

    `id: Any`
    :   Unique identifier for the status

    `name: Any`
    :   Name of the status

    `rank: Any`
    :   Rank for ordering

    `updated_at: Any`
    :   When the status was last updated

<a id="IncidentStatusesContainsCondition"></a>

`IncidentStatusesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesEqCondition"></a>

`IncidentStatusesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesFuzzyCondition"></a>

`IncidentStatusesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesStringFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesGetParams"></a>

`IncidentStatusesGetParams(*args, **kwargs)`
:   Parameters for incident_statuses.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IncidentStatusesGtCondition"></a>

`IncidentStatusesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesGteCondition"></a>

`IncidentStatusesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesInCondition"></a>

`IncidentStatusesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesInFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesInFilter"></a>

`IncidentStatusesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: list[str]`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: list[str]`
    :   When the status was created

    `description: list[str]`
    :   Description of the status

    `id: list[str]`
    :   Unique identifier for the status

    `name: list[str]`
    :   Name of the status

    `rank: list[float]`
    :   Rank for ordering

    `updated_at: list[str]`
    :   When the status was last updated

<a id="IncidentStatusesKeywordCondition"></a>

`IncidentStatusesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesStringFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesLikeCondition"></a>

`IncidentStatusesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesStringFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesListParams"></a>

`IncidentStatusesListParams(*args, **kwargs)`
:   Parameters for incident_statuses.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IncidentStatusesLtCondition"></a>

`IncidentStatusesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesLteCondition"></a>

`IncidentStatusesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesNeqCondition"></a>

`IncidentStatusesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentStatusesNotCondition"></a>

`IncidentStatusesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyCondition`
    :   The type of the None singleton.

<a id="IncidentStatusesOrCondition"></a>

`IncidentStatusesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentStatusesSearchFilter"></a>

`IncidentStatusesSearchFilter(*args, **kwargs)`
:   Available fields for filtering incident_statuses search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: str | None`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: str | None`
    :   When the status was created

    `description: str | None`
    :   Description of the status

    `id: str | None`
    :   Unique identifier for the status

    `name: str | None`
    :   Name of the status

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the status was last updated

<a id="IncidentStatusesSearchQuery"></a>

`IncidentStatusesSearchQuery(*args, **kwargs)`
:   Search query for incident_statuses entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentStatusesSortFilter]`
    :   The type of the None singleton.

<a id="IncidentStatusesSortFilter"></a>

`IncidentStatusesSortFilter(*args, **kwargs)`
:   Available fields for sorting incident_statuses search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: Literal['asc', 'desc']`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: Literal['asc', 'desc']`
    :   When the status was created

    `description: Literal['asc', 'desc']`
    :   Description of the status

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the status

    `name: Literal['asc', 'desc']`
    :   Name of the status

    `rank: Literal['asc', 'desc']`
    :   Rank for ordering

    `updated_at: Literal['asc', 'desc']`
    :   When the status was last updated

<a id="IncidentStatusesStringFilter"></a>

`IncidentStatusesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `category: str`
    :   Category: triage, active, post-incident, closed, etc.

    `created_at: str`
    :   When the status was created

    `description: str`
    :   Description of the status

    `id: str`
    :   Unique identifier for the status

    `name: str`
    :   Name of the status

    `rank: str`
    :   Rank for ordering

    `updated_at: str`
    :   When the status was last updated

<a id="IncidentTimestampsAndCondition"></a>

`IncidentTimestampsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentTimestampsAnyCondition"></a>

`IncidentTimestampsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsAnyValueFilter"></a>

`IncidentTimestampsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Any`
    :   Unique identifier for the timestamp

    `name: Any`
    :   Name of the timestamp

    `rank: Any`
    :   Rank for ordering

<a id="IncidentTimestampsContainsCondition"></a>

`IncidentTimestampsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsEqCondition"></a>

`IncidentTimestampsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsFuzzyCondition"></a>

`IncidentTimestampsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsStringFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsGetParams"></a>

`IncidentTimestampsGetParams(*args, **kwargs)`
:   Parameters for incident_timestamps.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IncidentTimestampsGtCondition"></a>

`IncidentTimestampsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsGteCondition"></a>

`IncidentTimestampsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsInCondition"></a>

`IncidentTimestampsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsInFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsInFilter"></a>

`IncidentTimestampsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: list[str]`
    :   Unique identifier for the timestamp

    `name: list[str]`
    :   Name of the timestamp

    `rank: list[float]`
    :   Rank for ordering

<a id="IncidentTimestampsKeywordCondition"></a>

`IncidentTimestampsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsStringFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsLikeCondition"></a>

`IncidentTimestampsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsStringFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsListParams"></a>

`IncidentTimestampsListParams(*args, **kwargs)`
:   Parameters for incident_timestamps.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="IncidentTimestampsLtCondition"></a>

`IncidentTimestampsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsLteCondition"></a>

`IncidentTimestampsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsNeqCondition"></a>

`IncidentTimestampsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentTimestampsNotCondition"></a>

`IncidentTimestampsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyCondition`
    :   The type of the None singleton.

<a id="IncidentTimestampsOrCondition"></a>

`IncidentTimestampsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentTimestampsSearchFilter"></a>

`IncidentTimestampsSearchFilter(*args, **kwargs)`
:   Available fields for filtering incident_timestamps search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str | None`
    :   Unique identifier for the timestamp

    `name: str | None`
    :   Name of the timestamp

    `rank: float | None`
    :   Rank for ordering

<a id="IncidentTimestampsSearchQuery"></a>

`IncidentTimestampsSearchQuery(*args, **kwargs)`
:   Search query for incident_timestamps entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentTimestampsSortFilter]`
    :   The type of the None singleton.

<a id="IncidentTimestampsSortFilter"></a>

`IncidentTimestampsSortFilter(*args, **kwargs)`
:   Available fields for sorting incident_timestamps search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the timestamp

    `name: Literal['asc', 'desc']`
    :   Name of the timestamp

    `rank: Literal['asc', 'desc']`
    :   Rank for ordering

<a id="IncidentTimestampsStringFilter"></a>

`IncidentTimestampsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   Unique identifier for the timestamp

    `name: str`
    :   Name of the timestamp

    `rank: str`
    :   Rank for ordering

<a id="IncidentUpdatesAndCondition"></a>

`IncidentUpdatesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentUpdatesAnyCondition"></a>

`IncidentUpdatesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesAnyValueFilter"></a>

`IncidentUpdatesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the update was created

    `id: Any`
    :   Unique identifier for the incident update

    `incident_id: Any`
    :   ID of the incident this update belongs to

    `message: Any`
    :   Update message content

    `new_incident_status: Any`
    :   New incident status set by this update

    `new_severity: Any`
    :   New severity set by this update

    `updater: Any`
    :   Who made this update

<a id="IncidentUpdatesContainsCondition"></a>

`IncidentUpdatesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesEqCondition"></a>

`IncidentUpdatesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesFuzzyCondition"></a>

`IncidentUpdatesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesStringFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesGtCondition"></a>

`IncidentUpdatesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesGteCondition"></a>

`IncidentUpdatesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesInCondition"></a>

`IncidentUpdatesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesInFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesInFilter"></a>

`IncidentUpdatesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the update was created

    `id: list[str]`
    :   Unique identifier for the incident update

    `incident_id: list[str]`
    :   ID of the incident this update belongs to

    `message: list[str]`
    :   Update message content

    `new_incident_status: list[dict[str, typing.Any]]`
    :   New incident status set by this update

    `new_severity: list[dict[str, typing.Any]]`
    :   New severity set by this update

    `updater: list[dict[str, typing.Any]]`
    :   Who made this update

<a id="IncidentUpdatesKeywordCondition"></a>

`IncidentUpdatesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesStringFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesLikeCondition"></a>

`IncidentUpdatesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesStringFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesListParams"></a>

`IncidentUpdatesListParams(*args, **kwargs)`
:   Parameters for incident_updates.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="IncidentUpdatesLtCondition"></a>

`IncidentUpdatesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesLteCondition"></a>

`IncidentUpdatesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesNeqCondition"></a>

`IncidentUpdatesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSearchFilter`
    :   The type of the None singleton.

<a id="IncidentUpdatesNotCondition"></a>

`IncidentUpdatesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyCondition`
    :   The type of the None singleton.

<a id="IncidentUpdatesOrCondition"></a>

`IncidentUpdatesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentUpdatesSearchFilter"></a>

`IncidentUpdatesSearchFilter(*args, **kwargs)`
:   Available fields for filtering incident_updates search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the update was created

    `id: str | None`
    :   Unique identifier for the incident update

    `incident_id: str | None`
    :   ID of the incident this update belongs to

    `message: str | None`
    :   Update message content

    `new_incident_status: dict[str, typing.Any] | None`
    :   New incident status set by this update

    `new_severity: dict[str, typing.Any] | None`
    :   New severity set by this update

    `updater: dict[str, typing.Any] | None`
    :   Who made this update

<a id="IncidentUpdatesSearchQuery"></a>

`IncidentUpdatesSearchQuery(*args, **kwargs)`
:   Search query for incident_updates entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentUpdatesSortFilter]`
    :   The type of the None singleton.

<a id="IncidentUpdatesSortFilter"></a>

`IncidentUpdatesSortFilter(*args, **kwargs)`
:   Available fields for sorting incident_updates search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the update was created

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the incident update

    `incident_id: Literal['asc', 'desc']`
    :   ID of the incident this update belongs to

    `message: Literal['asc', 'desc']`
    :   Update message content

    `new_incident_status: Literal['asc', 'desc']`
    :   New incident status set by this update

    `new_severity: Literal['asc', 'desc']`
    :   New severity set by this update

    `updater: Literal['asc', 'desc']`
    :   Who made this update

<a id="IncidentUpdatesStringFilter"></a>

`IncidentUpdatesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the update was created

    `id: str`
    :   Unique identifier for the incident update

    `incident_id: str`
    :   ID of the incident this update belongs to

    `message: str`
    :   Update message content

    `new_incident_status: str`
    :   New incident status set by this update

    `new_severity: str`
    :   New severity set by this update

    `updater: str`
    :   Who made this update

<a id="IncidentsAndCondition"></a>

`IncidentsAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentsAnyCondition"></a>

`IncidentsAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentsAnyValueFilter"></a>

`IncidentsAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the incident was created

    `creator: Any`
    :   The user who created the incident

    `custom_field_entries: Any`
    :   Custom field values for the incident

    `duration_metrics: Any`
    :   Duration metrics associated with the incident

    `has_debrief: Any`
    :   Whether the incident has had a debrief

    `id: Any`
    :   Unique identifier for the incident

    `incident_role_assignments: Any`
    :   Role assignments for the incident

    `incident_status: Any`
    :   Current status of the incident

    `incident_timestamp_values: Any`
    :   Timestamp values for the incident

    `incident_type: Any`
    :   Type of the incident

    `mode: Any`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `name: Any`
    :   Name/title of the incident

    `permalink: Any`
    :   Link to the incident in the dashboard

    `reference: Any`
    :   Human-readable reference (e.g. INC-123)

    `severity: Any`
    :   Severity of the incident

    `slack_channel_id: Any`
    :   Slack channel ID for the incident

    `slack_channel_name: Any`
    :   Slack channel name for the incident

    `slack_team_id: Any`
    :   Slack team/workspace ID

    `summary: Any`
    :   Detailed summary of the incident

    `updated_at: Any`
    :   When the incident was last updated

    `visibility: Any`
    :   Whether the incident is public or private

    `workload_minutes_late: Any`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: Any`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: Any`
    :   Total workload minutes

    `workload_minutes_working: Any`
    :   Minutes of workload classified as working

<a id="IncidentsContainsCondition"></a>

`IncidentsContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyValueFilter`
    :   The type of the None singleton.

<a id="IncidentsEqCondition"></a>

`IncidentsEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsFuzzyCondition"></a>

`IncidentsFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.IncidentsStringFilter`
    :   The type of the None singleton.

<a id="IncidentsGetParams"></a>

`IncidentsGetParams(*args, **kwargs)`
:   Parameters for incidents.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="IncidentsGtCondition"></a>

`IncidentsGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsGteCondition"></a>

`IncidentsGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsInCondition"></a>

`IncidentsInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.IncidentsInFilter`
    :   The type of the None singleton.

<a id="IncidentsInFilter"></a>

`IncidentsInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the incident was created

    `creator: list[dict[str, typing.Any]]`
    :   The user who created the incident

    `custom_field_entries: list[list[typing.Any]]`
    :   Custom field values for the incident

    `duration_metrics: list[list[typing.Any]]`
    :   Duration metrics associated with the incident

    `has_debrief: list[bool]`
    :   Whether the incident has had a debrief

    `id: list[str]`
    :   Unique identifier for the incident

    `incident_role_assignments: list[list[typing.Any]]`
    :   Role assignments for the incident

    `incident_status: list[dict[str, typing.Any]]`
    :   Current status of the incident

    `incident_timestamp_values: list[list[typing.Any]]`
    :   Timestamp values for the incident

    `incident_type: list[dict[str, typing.Any]]`
    :   Type of the incident

    `mode: list[str]`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `name: list[str]`
    :   Name/title of the incident

    `permalink: list[str]`
    :   Link to the incident in the dashboard

    `reference: list[str]`
    :   Human-readable reference (e.g. INC-123)

    `severity: list[dict[str, typing.Any]]`
    :   Severity of the incident

    `slack_channel_id: list[str]`
    :   Slack channel ID for the incident

    `slack_channel_name: list[str]`
    :   Slack channel name for the incident

    `slack_team_id: list[str]`
    :   Slack team/workspace ID

    `summary: list[str]`
    :   Detailed summary of the incident

    `updated_at: list[str]`
    :   When the incident was last updated

    `visibility: list[str]`
    :   Whether the incident is public or private

    `workload_minutes_late: list[float]`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: list[float]`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: list[float]`
    :   Total workload minutes

    `workload_minutes_working: list[float]`
    :   Minutes of workload classified as working

<a id="IncidentsKeywordCondition"></a>

`IncidentsKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.IncidentsStringFilter`
    :   The type of the None singleton.

<a id="IncidentsLikeCondition"></a>

`IncidentsLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.IncidentsStringFilter`
    :   The type of the None singleton.

<a id="IncidentsListParams"></a>

`IncidentsListParams(*args, **kwargs)`
:   Parameters for incidents.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="IncidentsLtCondition"></a>

`IncidentsLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsLteCondition"></a>

`IncidentsLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsNeqCondition"></a>

`IncidentsNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.IncidentsSearchFilter`
    :   The type of the None singleton.

<a id="IncidentsNotCondition"></a>

`IncidentsNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.IncidentsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyCondition`
    :   The type of the None singleton.

<a id="IncidentsOrCondition"></a>

`IncidentsOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyCondition]`
    :   The type of the None singleton.

<a id="IncidentsSearchFilter"></a>

`IncidentsSearchFilter(*args, **kwargs)`
:   Available fields for filtering incidents search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the incident was created

    `creator: dict[str, typing.Any] | None`
    :   The user who created the incident

    `custom_field_entries: list[typing.Any] | None`
    :   Custom field values for the incident

    `duration_metrics: list[typing.Any] | None`
    :   Duration metrics associated with the incident

    `has_debrief: bool | None`
    :   Whether the incident has had a debrief

    `id: str | None`
    :   Unique identifier for the incident

    `incident_role_assignments: list[typing.Any] | None`
    :   Role assignments for the incident

    `incident_status: dict[str, typing.Any] | None`
    :   Current status of the incident

    `incident_timestamp_values: list[typing.Any] | None`
    :   Timestamp values for the incident

    `incident_type: dict[str, typing.Any] | None`
    :   Type of the incident

    `mode: str | None`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `name: str | None`
    :   Name/title of the incident

    `permalink: str | None`
    :   Link to the incident in the dashboard

    `reference: str | None`
    :   Human-readable reference (e.g. INC-123)

    `severity: dict[str, typing.Any] | None`
    :   Severity of the incident

    `slack_channel_id: str | None`
    :   Slack channel ID for the incident

    `slack_channel_name: str | None`
    :   Slack channel name for the incident

    `slack_team_id: str | None`
    :   Slack team/workspace ID

    `summary: str | None`
    :   Detailed summary of the incident

    `updated_at: str | None`
    :   When the incident was last updated

    `visibility: str | None`
    :   Whether the incident is public or private

    `workload_minutes_late: float | None`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: float | None`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: float | None`
    :   Total workload minutes

    `workload_minutes_working: float | None`
    :   Minutes of workload classified as working

<a id="IncidentsSearchQuery"></a>

`IncidentsSearchQuery(*args, **kwargs)`
:   Search query for incidents entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.IncidentsEqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsGteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLtCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLteCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsInCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsNotCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAndCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsOrCondition | airbyte_agent_sdk.connectors.incident_io.types.IncidentsAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.IncidentsSortFilter]`
    :   The type of the None singleton.

<a id="IncidentsSortFilter"></a>

`IncidentsSortFilter(*args, **kwargs)`
:   Available fields for sorting incidents search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the incident was created

    `creator: Literal['asc', 'desc']`
    :   The user who created the incident

    `custom_field_entries: Literal['asc', 'desc']`
    :   Custom field values for the incident

    `duration_metrics: Literal['asc', 'desc']`
    :   Duration metrics associated with the incident

    `has_debrief: Literal['asc', 'desc']`
    :   Whether the incident has had a debrief

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the incident

    `incident_role_assignments: Literal['asc', 'desc']`
    :   Role assignments for the incident

    `incident_status: Literal['asc', 'desc']`
    :   Current status of the incident

    `incident_timestamp_values: Literal['asc', 'desc']`
    :   Timestamp values for the incident

    `incident_type: Literal['asc', 'desc']`
    :   Type of the incident

    `mode: Literal['asc', 'desc']`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `name: Literal['asc', 'desc']`
    :   Name/title of the incident

    `permalink: Literal['asc', 'desc']`
    :   Link to the incident in the dashboard

    `reference: Literal['asc', 'desc']`
    :   Human-readable reference (e.g. INC-123)

    `severity: Literal['asc', 'desc']`
    :   Severity of the incident

    `slack_channel_id: Literal['asc', 'desc']`
    :   Slack channel ID for the incident

    `slack_channel_name: Literal['asc', 'desc']`
    :   Slack channel name for the incident

    `slack_team_id: Literal['asc', 'desc']`
    :   Slack team/workspace ID

    `summary: Literal['asc', 'desc']`
    :   Detailed summary of the incident

    `updated_at: Literal['asc', 'desc']`
    :   When the incident was last updated

    `visibility: Literal['asc', 'desc']`
    :   Whether the incident is public or private

    `workload_minutes_late: Literal['asc', 'desc']`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: Literal['asc', 'desc']`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: Literal['asc', 'desc']`
    :   Total workload minutes

    `workload_minutes_working: Literal['asc', 'desc']`
    :   Minutes of workload classified as working

<a id="IncidentsStringFilter"></a>

`IncidentsStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the incident was created

    `creator: str`
    :   The user who created the incident

    `custom_field_entries: str`
    :   Custom field values for the incident

    `duration_metrics: str`
    :   Duration metrics associated with the incident

    `has_debrief: str`
    :   Whether the incident has had a debrief

    `id: str`
    :   Unique identifier for the incident

    `incident_role_assignments: str`
    :   Role assignments for the incident

    `incident_status: str`
    :   Current status of the incident

    `incident_timestamp_values: str`
    :   Timestamp values for the incident

    `incident_type: str`
    :   Type of the incident

    `mode: str`
    :   Mode of the incident: standard, retrospective, test, or tutorial

    `name: str`
    :   Name/title of the incident

    `permalink: str`
    :   Link to the incident in the dashboard

    `reference: str`
    :   Human-readable reference (e.g. INC-123)

    `severity: str`
    :   Severity of the incident

    `slack_channel_id: str`
    :   Slack channel ID for the incident

    `slack_channel_name: str`
    :   Slack channel name for the incident

    `slack_team_id: str`
    :   Slack team/workspace ID

    `summary: str`
    :   Detailed summary of the incident

    `updated_at: str`
    :   When the incident was last updated

    `visibility: str`
    :   Whether the incident is public or private

    `workload_minutes_late: str`
    :   Minutes of workload classified as late

    `workload_minutes_sleeping: str`
    :   Minutes of workload classified as sleeping

    `workload_minutes_total: str`
    :   Total workload minutes

    `workload_minutes_working: str`
    :   Minutes of workload classified as working

<a id="SchedulesAndCondition"></a>

`SchedulesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.SchedulesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyCondition]`
    :   The type of the None singleton.

<a id="SchedulesAnyCondition"></a>

`SchedulesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyValueFilter`
    :   The type of the None singleton.

<a id="SchedulesAnyValueFilter"></a>

`SchedulesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Any`
    :   Annotations metadata

    `config: Any`
    :   Schedule configuration with rotations

    `created_at: Any`
    :   When the schedule was created

    `current_shifts: Any`
    :   Currently active shifts

    `id: Any`
    :   Unique identifier for the schedule

    `name: Any`
    :   Name of the schedule

    `timezone: Any`
    :   Timezone for the schedule

    `updated_at: Any`
    :   When the schedule was last updated

<a id="SchedulesContainsCondition"></a>

`SchedulesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyValueFilter`
    :   The type of the None singleton.

<a id="SchedulesEqCondition"></a>

`SchedulesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesFuzzyCondition"></a>

`SchedulesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.SchedulesStringFilter`
    :   The type of the None singleton.

<a id="SchedulesGetParams"></a>

`SchedulesGetParams(*args, **kwargs)`
:   Parameters for schedules.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SchedulesGtCondition"></a>

`SchedulesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesGteCondition"></a>

`SchedulesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesInCondition"></a>

`SchedulesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.SchedulesInFilter`
    :   The type of the None singleton.

<a id="SchedulesInFilter"></a>

`SchedulesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: list[dict[str, typing.Any]]`
    :   Annotations metadata

    `config: list[dict[str, typing.Any]]`
    :   Schedule configuration with rotations

    `created_at: list[str]`
    :   When the schedule was created

    `current_shifts: list[list[typing.Any]]`
    :   Currently active shifts

    `id: list[str]`
    :   Unique identifier for the schedule

    `name: list[str]`
    :   Name of the schedule

    `timezone: list[str]`
    :   Timezone for the schedule

    `updated_at: list[str]`
    :   When the schedule was last updated

<a id="SchedulesKeywordCondition"></a>

`SchedulesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.SchedulesStringFilter`
    :   The type of the None singleton.

<a id="SchedulesLikeCondition"></a>

`SchedulesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.SchedulesStringFilter`
    :   The type of the None singleton.

<a id="SchedulesListParams"></a>

`SchedulesListParams(*args, **kwargs)`
:   Parameters for schedules.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="SchedulesLtCondition"></a>

`SchedulesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesLteCondition"></a>

`SchedulesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesNeqCondition"></a>

`SchedulesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.SchedulesSearchFilter`
    :   The type of the None singleton.

<a id="SchedulesNotCondition"></a>

`SchedulesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.SchedulesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyCondition`
    :   The type of the None singleton.

<a id="SchedulesOrCondition"></a>

`SchedulesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.SchedulesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyCondition]`
    :   The type of the None singleton.

<a id="SchedulesSearchFilter"></a>

`SchedulesSearchFilter(*args, **kwargs)`
:   Available fields for filtering schedules search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: dict[str, typing.Any] | None`
    :   Annotations metadata

    `config: dict[str, typing.Any] | None`
    :   Schedule configuration with rotations

    `created_at: str | None`
    :   When the schedule was created

    `current_shifts: list[typing.Any] | None`
    :   Currently active shifts

    `id: str | None`
    :   Unique identifier for the schedule

    `name: str | None`
    :   Name of the schedule

    `timezone: str | None`
    :   Timezone for the schedule

    `updated_at: str | None`
    :   When the schedule was last updated

<a id="SchedulesSearchQuery"></a>

`SchedulesSearchQuery(*args, **kwargs)`
:   Search query for schedules entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.SchedulesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SchedulesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.SchedulesSortFilter]`
    :   The type of the None singleton.

<a id="SchedulesSortFilter"></a>

`SchedulesSortFilter(*args, **kwargs)`
:   Available fields for sorting schedules search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: Literal['asc', 'desc']`
    :   Annotations metadata

    `config: Literal['asc', 'desc']`
    :   Schedule configuration with rotations

    `created_at: Literal['asc', 'desc']`
    :   When the schedule was created

    `current_shifts: Literal['asc', 'desc']`
    :   Currently active shifts

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the schedule

    `name: Literal['asc', 'desc']`
    :   Name of the schedule

    `timezone: Literal['asc', 'desc']`
    :   Timezone for the schedule

    `updated_at: Literal['asc', 'desc']`
    :   When the schedule was last updated

<a id="SchedulesStringFilter"></a>

`SchedulesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `annotations: str`
    :   Annotations metadata

    `config: str`
    :   Schedule configuration with rotations

    `created_at: str`
    :   When the schedule was created

    `current_shifts: str`
    :   Currently active shifts

    `id: str`
    :   Unique identifier for the schedule

    `name: str`
    :   Name of the schedule

    `timezone: str`
    :   Timezone for the schedule

    `updated_at: str`
    :   When the schedule was last updated

<a id="SeveritiesAndCondition"></a>

`SeveritiesAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.SeveritiesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyCondition]`
    :   The type of the None singleton.

<a id="SeveritiesAnyCondition"></a>

`SeveritiesAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyValueFilter`
    :   The type of the None singleton.

<a id="SeveritiesAnyValueFilter"></a>

`SeveritiesAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Any`
    :   When the severity was created

    `description: Any`
    :   Description of the severity

    `id: Any`
    :   Unique identifier for the severity

    `name: Any`
    :   Name of the severity

    `rank: Any`
    :   Rank for ordering

    `updated_at: Any`
    :   When the severity was last updated

<a id="SeveritiesContainsCondition"></a>

`SeveritiesContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyValueFilter`
    :   The type of the None singleton.

<a id="SeveritiesEqCondition"></a>

`SeveritiesEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesFuzzyCondition"></a>

`SeveritiesFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesStringFilter`
    :   The type of the None singleton.

<a id="SeveritiesGetParams"></a>

`SeveritiesGetParams(*args, **kwargs)`
:   Parameters for severities.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="SeveritiesGtCondition"></a>

`SeveritiesGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesGteCondition"></a>

`SeveritiesGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesInCondition"></a>

`SeveritiesInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesInFilter`
    :   The type of the None singleton.

<a id="SeveritiesInFilter"></a>

`SeveritiesInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: list[str]`
    :   When the severity was created

    `description: list[str]`
    :   Description of the severity

    `id: list[str]`
    :   Unique identifier for the severity

    `name: list[str]`
    :   Name of the severity

    `rank: list[float]`
    :   Rank for ordering

    `updated_at: list[str]`
    :   When the severity was last updated

<a id="SeveritiesKeywordCondition"></a>

`SeveritiesKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesStringFilter`
    :   The type of the None singleton.

<a id="SeveritiesLikeCondition"></a>

`SeveritiesLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesStringFilter`
    :   The type of the None singleton.

<a id="SeveritiesListParams"></a>

`SeveritiesListParams(*args, **kwargs)`
:   Parameters for severities.list operation

    ### Ancestors (in MRO)

    * builtins.dict

<a id="SeveritiesLtCondition"></a>

`SeveritiesLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesLteCondition"></a>

`SeveritiesLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesNeqCondition"></a>

`SeveritiesNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSearchFilter`
    :   The type of the None singleton.

<a id="SeveritiesNotCondition"></a>

`SeveritiesNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyCondition`
    :   The type of the None singleton.

<a id="SeveritiesOrCondition"></a>

`SeveritiesOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.SeveritiesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyCondition]`
    :   The type of the None singleton.

<a id="SeveritiesSearchFilter"></a>

`SeveritiesSearchFilter(*args, **kwargs)`
:   Available fields for filtering severities search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str | None`
    :   When the severity was created

    `description: str | None`
    :   Description of the severity

    `id: str | None`
    :   Unique identifier for the severity

    `name: str | None`
    :   Name of the severity

    `rank: float | None`
    :   Rank for ordering

    `updated_at: str | None`
    :   When the severity was last updated

<a id="SeveritiesSearchQuery"></a>

`SeveritiesSearchQuery(*args, **kwargs)`
:   Search query for severities entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.SeveritiesEqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesGteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLtCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLteCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesInCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesNotCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAndCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesOrCondition | airbyte_agent_sdk.connectors.incident_io.types.SeveritiesAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.SeveritiesSortFilter]`
    :   The type of the None singleton.

<a id="SeveritiesSortFilter"></a>

`SeveritiesSortFilter(*args, **kwargs)`
:   Available fields for sorting severities search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: Literal['asc', 'desc']`
    :   When the severity was created

    `description: Literal['asc', 'desc']`
    :   Description of the severity

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the severity

    `name: Literal['asc', 'desc']`
    :   Name of the severity

    `rank: Literal['asc', 'desc']`
    :   Rank for ordering

    `updated_at: Literal['asc', 'desc']`
    :   When the severity was last updated

<a id="SeveritiesStringFilter"></a>

`SeveritiesStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `created_at: str`
    :   When the severity was created

    `description: str`
    :   Description of the severity

    `id: str`
    :   Unique identifier for the severity

    `name: str`
    :   Name of the severity

    `rank: str`
    :   Rank for ordering

    `updated_at: str`
    :   When the severity was last updated

<a id="UsersAndCondition"></a>

`UsersAndCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `and: list[airbyte_agent_sdk.connectors.incident_io.types.UsersEqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersInCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNotCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAndCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersOrCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersAnyCondition"></a>

`UsersAnyCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `any: airbyte_agent_sdk.connectors.incident_io.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersAnyValueFilter"></a>

`UsersAnyValueFilter(*args, **kwargs)`
:   Available fields with Any value type. Used for 'contains' and 'any' conditions.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_role: Any`
    :   Base role assigned to the user

    `custom_roles: Any`
    :   Custom roles assigned to the user

    `email: Any`
    :   Email address of the user

    `id: Any`
    :   Unique identifier for the user

    `name: Any`
    :   Full name of the user

    `role: Any`
    :   Deprecated role field

    `slack_user_id: Any`
    :   Slack user ID

<a id="UsersContainsCondition"></a>

`UsersContainsCondition(*args, **kwargs)`
:   Check if value exists in array field. Example: \{"contains": \{"tags": "premium"\}\}

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `contains: airbyte_agent_sdk.connectors.incident_io.types.UsersAnyValueFilter`
    :   The type of the None singleton.

<a id="UsersEqCondition"></a>

`UsersEqCondition(*args, **kwargs)`
:   Equal to: field equals value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `eq: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersFuzzyCondition"></a>

`UsersFuzzyCondition(*args, **kwargs)`
:   Ordered word text match (case-insensitive).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `fuzzy: airbyte_agent_sdk.connectors.incident_io.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersGetParams"></a>

`UsersGetParams(*args, **kwargs)`
:   Parameters for users.get operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `id: str`
    :   The type of the None singleton.

<a id="UsersGtCondition"></a>

`UsersGtCondition(*args, **kwargs)`
:   Greater than: field > value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gt: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersGteCondition"></a>

`UsersGteCondition(*args, **kwargs)`
:   Greater than or equal: field >= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `gte: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersInCondition"></a>

`UsersInCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `in: airbyte_agent_sdk.connectors.incident_io.types.UsersInFilter`
    :   The type of the None singleton.

<a id="UsersInFilter"></a>

`UsersInFilter(*args, **kwargs)`
:   Available fields for 'in' condition (values are lists).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_role: list[dict[str, typing.Any]]`
    :   Base role assigned to the user

    `custom_roles: list[list[typing.Any]]`
    :   Custom roles assigned to the user

    `email: list[str]`
    :   Email address of the user

    `id: list[str]`
    :   Unique identifier for the user

    `name: list[str]`
    :   Full name of the user

    `role: list[str]`
    :   Deprecated role field

    `slack_user_id: list[str]`
    :   Slack user ID

<a id="UsersKeywordCondition"></a>

`UsersKeywordCondition(*args, **kwargs)`
:   Keyword text match (any word present).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `keyword: airbyte_agent_sdk.connectors.incident_io.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersLikeCondition"></a>

`UsersLikeCondition(*args, **kwargs)`
:   Partial string match with % wildcards.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `like: airbyte_agent_sdk.connectors.incident_io.types.UsersStringFilter`
    :   The type of the None singleton.

<a id="UsersListParams"></a>

`UsersListParams(*args, **kwargs)`
:   Parameters for users.list operation

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `after: str`
    :   The type of the None singleton.

    `page_size: int`
    :   The type of the None singleton.

<a id="UsersLtCondition"></a>

`UsersLtCondition(*args, **kwargs)`
:   Less than: field &lt; value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lt: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersLteCondition"></a>

`UsersLteCondition(*args, **kwargs)`
:   Less than or equal: field &lt;= value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `lte: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNeqCondition"></a>

`UsersNeqCondition(*args, **kwargs)`
:   Not equal to: field does not equal value.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `neq: airbyte_agent_sdk.connectors.incident_io.types.UsersSearchFilter`
    :   The type of the None singleton.

<a id="UsersNotCondition"></a>

`UsersNotCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `not: airbyte_agent_sdk.connectors.incident_io.types.UsersEqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersInCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNotCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAndCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersOrCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAnyCondition`
    :   The type of the None singleton.

<a id="UsersOrCondition"></a>

`UsersOrCondition(*args, **kwargs)`
:   dict() -> new empty dictionary
    dict(mapping) -> new dictionary initialized from a mapping object's
        (key, value) pairs
    dict(iterable) -> new dictionary initialized as if via:
        d = \{\}
        for k, v in iterable:
            d[k] = v
    dict(**kwargs) -> new dictionary initialized with the name=value pairs
        in the keyword argument list.  For example:  dict(one=1, two=2)

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `or: list[airbyte_agent_sdk.connectors.incident_io.types.UsersEqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersInCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNotCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAndCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersOrCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAnyCondition]`
    :   The type of the None singleton.

<a id="UsersSearchFilter"></a>

`UsersSearchFilter(*args, **kwargs)`
:   Available fields for filtering users search queries.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_role: dict[str, typing.Any] | None`
    :   Base role assigned to the user

    `custom_roles: list[typing.Any] | None`
    :   Custom roles assigned to the user

    `email: str | None`
    :   Email address of the user

    `id: str | None`
    :   Unique identifier for the user

    `name: str | None`
    :   Full name of the user

    `role: str | None`
    :   Deprecated role field

    `slack_user_id: str | None`
    :   Slack user ID

<a id="UsersSearchQuery"></a>

`UsersSearchQuery(*args, **kwargs)`
:   Search query for users entity.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `filter: airbyte_agent_sdk.connectors.incident_io.types.UsersEqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNeqCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersGteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLtCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLteCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersInCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersLikeCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersFuzzyCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersKeywordCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersContainsCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersNotCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAndCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersOrCondition | airbyte_agent_sdk.connectors.incident_io.types.UsersAnyCondition`
    :   The type of the None singleton.

    `sort: list[airbyte_agent_sdk.connectors.incident_io.types.UsersSortFilter]`
    :   The type of the None singleton.

<a id="UsersSortFilter"></a>

`UsersSortFilter(*args, **kwargs)`
:   Available fields for sorting users search results.

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_role: Literal['asc', 'desc']`
    :   Base role assigned to the user

    `custom_roles: Literal['asc', 'desc']`
    :   Custom roles assigned to the user

    `email: Literal['asc', 'desc']`
    :   Email address of the user

    `id: Literal['asc', 'desc']`
    :   Unique identifier for the user

    `name: Literal['asc', 'desc']`
    :   Full name of the user

    `role: Literal['asc', 'desc']`
    :   Deprecated role field

    `slack_user_id: Literal['asc', 'desc']`
    :   Slack user ID

<a id="UsersStringFilter"></a>

`UsersStringFilter(*args, **kwargs)`
:   String fields for text search conditions (like, fuzzy, keyword).

    ### Ancestors (in MRO)

    * builtins.dict

    ### Class variables

    `base_role: str`
    :   Base role assigned to the user

    `custom_roles: str`
    :   Custom roles assigned to the user

    `email: str`
    :   Email address of the user

    `id: str`
    :   Unique identifier for the user

    `name: str`
    :   Full name of the user

    `role: str`
    :   Deprecated role field

    `slack_user_id: str`
    :   Slack user ID