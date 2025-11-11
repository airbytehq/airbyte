from typing import Any, Mapping, Optional

from airbyte_cdk.sources.declarative.schema import SchemaLoader


class CachingSchemaLoaderDecorator(SchemaLoader):
    def __init__(self, schema_loader: SchemaLoader):
        self._decorated = schema_loader
        self._loaded_schema: Optional[Mapping[str, Any]] = None

    def get_json_schema(self) -> Mapping[str, Any]:
        if self._loaded_schema is None:
            self._loaded_schema = self._decorated.get_json_schema()

        return self._loaded_schema  # type: ignore  # at that point, we assume the schema will be populated
