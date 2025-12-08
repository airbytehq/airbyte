SEARCH_API_MAX_LIMIT = 200  # Limit of 200 max

# These fields are implied to be common to all objects in Close
# https://developer.close.com/resources/advanced-filtering/#visual-query-builder:~:text=user_def%22%5D%0A%7D-,Most%20commonly%20used%20fields,-For%20Contact%3A
COMMON_FIELDS = [
    {"id": "id", "type": {"type": "string"}},
    {"id": "name", "type": {"type": "string"}},
    {"id": "date_created", "type": {"type": "string", "format": "date-time"}},
    {"id": "date_updated", "type": {"type": "string", "format": "date-time"}},
    {"id": "updated_by", "type": {"type": "string"}},
    {"id": "created_by", "type": {"type": "string"}},
]

CUSTOM_FIELD_PREFIX = "custom."
