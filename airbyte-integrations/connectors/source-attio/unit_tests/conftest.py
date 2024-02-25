import pytest

from uuid import uuid4


@pytest.fixture
def make_object_response():
    def make(workspace_id: str, api_slug: str, singular_noun: str, plural_noun: str, object_id: str = None) -> dict:
        object_id = object_id or str(uuid4())
        return {
            "id": {"workspace_id": workspace_id, "object_id": object_id},
            "api_slug": api_slug,
            "singular_noun": singular_noun,
            "plural_noun": plural_noun,
            "created_at": "2023-03-13T23:20:19.285000000Z",
        }

    return make


@pytest.fixture
def make_attribute_response():
    def make(
        type: str,
        workspace_id: str,
        object_id: str,
        is_multi: bool,
        attribute_id: str = None,
        title: str = None,
        api_slug: str = None,
        allowed_object_ids: list = None,
    ) -> dict:
        attribute_id = attribute_id or str(uuid4())
        title = title or f"{type} {'(multi)' if is_multi else ''} attribute"
        api_slug = api_slug or f"{type}_{'multi' if is_multi else 'single'}_attribute"
        description = f"{type} {'(multi)' if is_multi else ''} description"

        return {
            "id": {
                "workspace_id": workspace_id,
                "object_id": object_id,
                "attribute_id": attribute_id,
            },
            "title": title,
            "description": description,
            "api_slug": api_slug,
            "type": type,
            "is_system_attribute": False,
            "is_writable": True,
            "is_required": False,
            "is_unique": False,
            "is_multiselect": is_multi,
            "is_default_value_enabled": False,
            "is_writable": True,
            "is_archived": False,
            "default_value": None,
            "relationship": None,
            "created_at": "2023-03-13T23:20:19.285000000Z",
            "config": {
                "currency": {"default_currency_code": None, "display_type": None},
                "record_reference": {"allowed_object_ids": allowed_object_ids},
            },
        }

    return make


@pytest.fixture
def make_record_response():
    def make(
        workspace_id: str,
        object_id: str,
        record_id=None,
        values={},
    ) -> dict:
        record_id = record_id or str(uuid4())
        return {
            "id": {
                "workspace_id": workspace_id,
                "object_id": object_id,
                "record_id": record_id,
            },
            "values": values,
            "created_at": "2023-03-13T23:20:19.285000000Z",
        }

    return make
