from typing import Any, Mapping, Optional
from source_close_com.constants import COMMON_FIELDS, CUSTOM_FIELD_PREFIX, SEARCH_API_MAX_LIMIT


def get_data_type(data: Mapping[str, Any]) -> Mapping[str, Any]:
    # Full list of data types here: https://developer.close.com/resources/custom-fields/
    data_type = data.get("type")
    match data_type:
        case "text" | "choices" | "textarea":
            return {"type": ["null", "string"]}
        case "number":
            return {"type": ["null", "number"]}
        case "date":
            return {"type": ["null", "string"], "format": "date"}
        case "datetime":
            return {"type": ["null", "string"], "format": "date-time"}
        case "user" | "custom_object":
            return {"type": ["null", "string", "number"]}
        case "hidden":
            return {"type": ["null", "string", "number", "boolean"]}
        case _:
            return {"type": ["string"]}


def generate_custom_object_search_query(
    object_id: str,
    created_date: str,
    fields: list[Mapping[str, Any]],
    updated_date: Optional[str] = None,
    updated_date_field: Optional[str] = None,
    cursor: Optional[str] = None,
) -> dict:
    """
    Generate a search query for a custom object type in Close.com.

    created_date: format YYYY-MM-DD, e.g. "2025-12-03"
    updated_date: format YYYY-MM-DD, e.g. "2025-12-04"
    fields: list of fields to include in the search, e.g. [{"id": "field_1", "type": "text"}, {"id": "field_2", "type": "number"}]
    """
    updated_date_condition = (
        [
            {
                "type": "field_condition",
                "field": {
                    "type": "regular_field",
                    "object_type": "custom_object",
                    "field_name": updated_date_field,
                },
                "condition": {
                    "before": None,
                    "on_or_after": {
                        "type": "fixed_local_date",
                        "value": updated_date,
                        "which": "start",
                    },
                    "type": "moment_range",
                },
            }
        ]
        if updated_date and updated_date_field
        else []
    )

    return {
        "query": {
            "type": "and",
            "queries": [
                {"type": "object_type", "object_type": "custom_object"},
                {
                    "type": "field_condition",
                    "field": {
                        "type": "regular_field",
                        "object_type": "custom_object",
                        "field_name": "custom_object_type_id",
                    },
                    "condition": {
                        "type": "term",
                        "values": [object_id],
                    },
                },
                {
                    "type": "field_condition",
                    "field": {
                        "type": "regular_field",
                        "object_type": "custom_object",
                        "field_name": "date_created",
                    },
                    # Use visual query builder to generate conditions
                    # There is very little documentation currently on the schema of the conditions/filters. So just build them manually in the UI and then copy as json.
                    # https://developer.close.com/resources/advanced-filtering/#visual-query-builder:~:text=to%20your%20needs.-,Visual%20Query%20Builder,triple%2Ddot%20menu%20on%20the%20top%20right%20and%20selecting%20%22Copy%20Filters%22.,-Output%20control
                    "condition": {
                        "before": None,
                        "on_or_after": {
                            "type": "fixed_local_date",
                            "value": created_date,
                            "which": "start",
                        },
                        "type": "moment_range",
                    },
                },
                *updated_date_condition,
            ],
        },
        **({"cursor": cursor} if cursor else {}),
        "_limit": SEARCH_API_MAX_LIMIT,
        "_fields": {
            "custom_object": [
                *[f["id"] for f in COMMON_FIELDS],
                *[f"{CUSTOM_FIELD_PREFIX}{f['id']}" for f in fields],
            ]
        },
    }
