#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Type

from airbyte_cdk.sources.utils.schema_helpers import expand_refs
from pydantic import BaseModel

class BaseSchemaModel(BaseModel):
    """
    Base class for all schema models. It has some extra schema postprocessing.
    """

    # TODO[pydantic]: We couldn't refactor this class, please create the `model_config` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    class Config:
        extra = "allow"

        @classmethod
        def schema_extra(cls, schema: Dict[str, Any], model: Type[BaseModel]) -> None:
            """Modify generated jsonschema, remove "title", "description" and "required" fields.

            Pydantic doesn't treat Union[None, Any] type correctly when generate jsonschema,
            so we can't set field as nullable (i.e. field that can have either null and non-null values),
            We generate this jsonschema value manually.

            :param schema: generated jsonschema
            :param model:
            """
            schema.pop("title", None)
            schema.pop("description", None)
            schema.pop("required", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                prop.pop("description", None)
                required = model.model_fields.get(name).is_required()
                if not required:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]

    @classmethod
    def schema(cls, *args, **kwargs) -> Dict[str, Any]:
        """We're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(*args, **kwargs)
        expand_refs(schema)
        return schema
