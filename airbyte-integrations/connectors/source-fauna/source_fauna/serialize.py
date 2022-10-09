#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

# Handles serializing any fauna document into an airbyte record

import base64
from datetime import date

from faunadb import _json
from faunadb.objects import FaunaTime, Query, Ref, SetRef


def fauna_doc_to_airbyte(doc: dict) -> dict:
    """
    Converts a full fauna document into the airbyte representation.

    This will mutate and return the input `doc`. If you don't want this behavior, deep copy
    the dict before passing it in.
    """
    for k, v in doc.items():
        doc[k] = _fauna_value_to_airbyte(v)
    return doc


def _fauna_value_to_airbyte(value: any) -> any:
    """
    Converts a fauna document to an airbyte-serializable document. This will simply replace
    all FaunaTime, Ref, dates, and byte arrays with native json objects.

    This will mutate `value` (if possible), and return the new `value`.
    """
    if isinstance(value, dict):
        for k, v in value.items():
            value[k] = _fauna_value_to_airbyte(v)
        return value
    elif isinstance(value, list):
        for i, v in enumerate(value):
            value[i] = _fauna_value_to_airbyte(v)
        return value
    elif isinstance(value, Ref):
        # serialize this however we feel like
        return ref_to_airbyte(value)
    elif isinstance(value, (Query, SetRef)):
        # for these we give up :P
        return _json.to_json(value)
    elif isinstance(value, FaunaTime):
        # this matches the airbyte `date-time` spec
        return value.value
    elif isinstance(value, date):
        # this matches the airbyte `date` spec
        return value.isoformat()
    elif isinstance(value, (bytes, bytearray)):
        # airbyte has no byte arrays, so this is just a string
        return base64.urlsafe_b64encode(value).decode("utf-8")
    else:
        # if its anything else, we don't mutate it, and let the json
        # serializer deal with it.
        return value


def ref_to_airbyte(ref) -> dict:
    # Note that the ref.database() field is never set, so we ignore it.
    if ref.collection() is None:
        # We have no nesting on this ref. Therefore, it is invalid, so
        # we return an unknown type.
        return {"id": ref.id(), "type": "unknown"}
    elif ref.collection().collection() is None:
        # We have a singly nested ref.
        # Example: Ref("my_collection", Ref("collections"))
        #      or: Ref("my_index", Ref("indexes"))
        collection_names = {
            "collections": "collection",
            "databases": "database",
            "indexes": "index",
            "functions": "function",
            "roles": "role",
            "access_providers": "access_provider",
            "keys": "key",
            "tokens": "token",
            "credentials": "credential",
        }
        return {
            "id": ref.id(),
            "type": collection_names.get(
                # Use the collection id as the key in the above map
                ref.collection().id(),
                # If that fails, we have an invalid ref, so we fallback to this id.
                ref.collection().id(),
            ),
        }
    elif (ref.collection().collection().collection() is None) and (ref.collection().collection().id() == "collections"):
        # This is a document.
        #
        # Example: Ref("1234", Ref("collection_name", Ref("collections")))
        return {
            "id": ref.id(),
            "collection": ref.collection().id(),
            "type": "document",
        }
    else:
        # We have a tripply nested ref, so we are in undefined behavior.
        #
        # Just try our best, and produce `type: unknown`
        return {
            "id": ref.id(),
            "type": "unknown",
        }
