#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict

from airbyte_cdk.sources.utils.schema_helpers import expand_refs, rename_key
from pydantic.v1 import BaseModel


class BaseConfig(BaseModel):
    """Base class for connector spec, adds the following behaviour:

    - resolve $ref and replace it with definition
    - replace all occurrences of anyOf with oneOf
    - drop description
    """

    @classmethod
    def schema(cls, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """We're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(*args, **kwargs)
        rename_key(schema, old_key="anyOf", new_key="oneOf")  # UI supports only oneOf
        expand_refs(schema)
        schema.pop("description", None)  # description added from the docstring
        return schema  # type: ignore[no-any-return]
