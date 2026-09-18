# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.http_config import MAX_CONNECTION_POOL_SIZE
from source_posthog.components import EventsRetriever, PosthogHTTPAdapter, PosthogRetriever


class PosthogComponentFactory(ModelToComponentFactory):
    def create_http_requester(self, model, config, **kwargs):
        requester = super().create_http_requester(model, config, **kwargs)
        for scheme in ("http://", "https://"):
            requester._session.mount(
                scheme,
                PosthogHTTPAdapter(pool_connections=MAX_CONNECTION_POOL_SIZE, pool_maxsize=MAX_CONNECTION_POOL_SIZE),
            )
        return requester

    def create_simple_retriever(self, model, config, **kwargs):
        retriever = super().create_simple_retriever(model, config, **kwargs)
        retriever_class = EventsRetriever if retriever.name == "events" else PosthogRetriever
        return retriever_class(
            requester=retriever.requester,
            record_selector=retriever.record_selector,
            config=config,
            parameters=model.parameters or {},
            name=retriever.name,
            primary_key=retriever.primary_key,
            paginator=retriever.paginator,
            stream_slicer=retriever.stream_slicer,
            cursor=retriever.cursor,
        )


class SourcePosthog(YamlDeclarativeSource):
    def __init__(self):
        self._path_to_yaml = "manifest.yaml"
        ManifestDeclarativeSource.__init__(
            self,
            self._read_and_parse_yaml_file(self._path_to_yaml),
            component_factory=PosthogComponentFactory(),
        )

    def read(self, logger, config, catalog, state=None):
        # Existing connections keep their saved catalog order after an upgrade.
        ordered_catalog = catalog.copy(update={"streams": sorted(catalog.streams, key=lambda stream: stream.stream.name == "persons")})
        yield from super().read(logger, config, ordered_catalog, state)
