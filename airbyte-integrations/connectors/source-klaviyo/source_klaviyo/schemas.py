#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from datetime import datetime
from typing import Any, Dict, List, MutableMapping, Optional

from jsonschema import RefResolver
from pydantic import BaseModel, Extra


class BaseSchemaModel(BaseModel):
    class Config:
        extra = Extra.allow

        @staticmethod
        def schema_extra(schema: MutableMapping[str, Any], model) -> None:
            # Pydantic adds a title to each attribute, that is not needed, so we manually drop them.
            # Also pydantic does not add a "null" option to a field marked as optional,
            # so we add this functionality manually. Same for "$ref"
            schema.pop("title", None)
            for name, prop in schema.get("properties", {}).items():
                prop.pop("title", None)
                allow_none = model.__fields__[name].allow_none
                if allow_none:
                    if "type" in prop:
                        prop["type"] = ["null", prop["type"]]
                    elif "$ref" in prop:
                        ref = prop.pop("$ref")
                        prop["oneOf"] = [{"type": "null"}, {"$ref": ref}]

    @classmethod
    def _expand_refs(cls, schema: Any, ref_resolver: Optional[RefResolver] = None) -> None:
        """Iterate over schema and replace all occurrences of $ref with their definitions. Recursive.

        :param schema: schema that will be patched
        :param ref_resolver: resolver to get definition from $ref, if None pass it will be instantiated
        """
        ref_resolver = ref_resolver or RefResolver.from_schema(schema)

        if isinstance(schema, MutableMapping):
            if "$ref" in schema:
                ref_url = schema.pop("$ref")
                _, definition = ref_resolver.resolve(ref_url)
                cls._expand_refs(definition, ref_resolver=ref_resolver)  # expand refs in definitions as well
                schema.update(definition)
            else:
                for key, value in schema.items():
                    cls._expand_refs(value, ref_resolver=ref_resolver)
        elif isinstance(schema, List):
            for value in schema:
                cls._expand_refs(value, ref_resolver=ref_resolver)

    @classmethod
    def schema(cls, **kwargs) -> Dict[str, Any]:
        """We're overriding the schema classmethod to enable some post-processing"""
        schema = super().schema(**kwargs)
        cls._expand_refs(schema)  # UI and destination doesn't support $ref's
        schema.pop("definitions", None)  # remove definitions created by $ref
        return schema

    object: str


class PersonList(BaseSchemaModel):
    id: str
    name: str
    created: datetime
    updated: datetime
    person_count: int
    list_type: str
    folder: Optional[str]


class Campaign(BaseSchemaModel):
    id: str
    name: str
    created: Optional[datetime]
    updated: Optional[datetime]
    status: str
    status_id: int
    status_label: str
    from_name: str
    from_email: str
    num_recipients: int
    lists: List[PersonList]
    excluded_lists: List[PersonList]
    is_segmented: bool
    send_time: Optional[datetime]
    sent_at: Optional[datetime]
    campaign_type: str
    subject: Optional[str]
    message_type: str
    template_id: Optional[str]


class Event(BaseSchemaModel):
    id: str
    uuid: str
    event_name: str
    timestamp: int
    datetime: str
    statistic_id: str
    event_properties: dict
    person: dict
    flow_id: Optional[str]
    campaign_id: Optional[str]
    flow_message_id: Optional[str]


class Flow(BaseSchemaModel):
    id: str
    name: str
    status: str
    created: datetime
    updated: datetime
    customer_filter: Optional[dict]
    trigger: dict


class GlobalExclusion(BaseSchemaModel):
    email: str
    reason: str
    timestamp: datetime


class Integration(BaseSchemaModel):
    id: str
    name: str
    category: str


class Metric(BaseSchemaModel):
    id: str
    name: str
    created: datetime
    updated: datetime
    integration: Integration
