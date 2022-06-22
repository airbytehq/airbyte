#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import copy
import importlib
from typing import Any, Mapping, get_type_hints

from airbyte_cdk.sources.declarative.checks.check_stream import CheckStream
from airbyte_cdk.sources.declarative.checks.connection_checker import ConnectionChecker
from airbyte_cdk.sources.declarative.create_partial import create
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.http_extractor import HttpExtractor
from airbyte_cdk.sources.declarative.extractors.jello import JelloExtractor
from airbyte_cdk.sources.declarative.interpolation.jinja import JinjaInterpolation
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.requester import Requester
from airbyte_cdk.sources.declarative.requesters.retriers.default_retrier import DefaultRetrier
from airbyte_cdk.sources.declarative.requesters.retriers.retrier import Retrier
from airbyte_cdk.sources.declarative.retrievers.retriever import Retriever
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.declarative.schema.json_schema import JsonSchema
from airbyte_cdk.sources.declarative.schema.schema_loader import SchemaLoader
from airbyte_cdk.sources.declarative.types import Config

class_registry = {
    "jq": "airbyte_cdk.sources.declarative.extractors.jq.JqExtractor",
    "NextPageUrlPaginator": "airbyte_cdk.sources.declarative.requesters.paginators.next_page_url_paginator.NextPageUrlPaginator",
    "InterpolatedPaginator": "airbyte_cdk.sources.declarative.requesters.paginators.interpolated_paginator.InterpolatedPaginator",
    "TokenAuthenticator": "airbyte_cdk.sources.streams.http.requests_native_auth.token.TokenAuthenticator",
}

default_implementations_registry = {
    Requester: HttpRequester,
    Retriever: SimpleRetriever,
    SchemaLoader: JsonSchema,
    HttpExtractor: JelloExtractor,
    ConnectionChecker: CheckStream,
    Retrier: DefaultRetrier,
    Decoder: JsonDecoder,
}


class DeclarativeComponentFactory:
    def __init__(self):
        self._interpolator = JinjaInterpolation()

    def create_component(self, component_definition: Mapping[str, Any], config: Config):
        """

        :param component_definition: mapping defining the object to create. It should have at least one field: `class_name`
        :param config: Connector's config
        :return: the object to create
        """
        kwargs = copy.deepcopy(component_definition)
        class_name = kwargs.pop("class_name")
        return self.build(class_name, config, **kwargs)

    def build(self, class_name: str, config, **kwargs):
        if isinstance(class_name, str):
            fqcn = class_name
            split = fqcn.split(".")
            module = ".".join(split[:-1])
            class_name = split[-1]
            class_ = getattr(importlib.import_module(module), class_name)
        else:
            class_ = class_name

        # create components in options before propagating them
        if "options" in kwargs:
            kwargs["options"] = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs["options"].items()}

        updated_kwargs = {k: self._create_subcomponent(k, v, kwargs, config, class_) for k, v in kwargs.items()}

        return create(class_, config=config, **updated_kwargs)

    def _merge_dicts(self, d1, d2):
        return {**d1, **d2}

    def _create_subcomponent(self, k, v, kwargs, config, parent_class):
        if isinstance(v, dict) and "class_name" in v:
            # propagate kwargs to inner objects
            v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))

            return self.create_component(v, config)()
        elif isinstance(v, dict) and "type" in v:
            v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))
            object_type = v.pop("type")
            class_name = class_registry[object_type]
            v["class_name"] = class_name
            return self.create_component(v, config)()
        elif isinstance(v, dict):
            # FIXME: remove try/catch
            try:
                t = k
                type_hints = get_type_hints(parent_class.__init__)
                interface = type_hints.get(t)
                expected_type = default_implementations_registry.get(interface)
                print(f"parent_class: {parent_class}")
                print(f"k: {k}")
                print(f"v: {v}")
                print(f"type_hints: {type_hints}")
                print(f"interface: {interface}")
                print(f"expected_type: {expected_type}")
                if expected_type:
                    v["class_name"] = expected_type
                    v["options"] = self._merge_dicts(kwargs.get("options", dict()), v.get("options", dict()))
                    return self.create_component(v, config)()
                else:
                    return v
            except Exception as e:
                print(f"failed to create {k}: {v} ({e})")
            return v
        elif isinstance(v, list):
            return [
                self._create_subcomponent(
                    k, sub, self._merge_dicts(kwargs.get("options", dict()), self._get_subcomponent_options(sub)), config, parent_class
                )
                for sub in v
            ]
        else:
            return v

    def _get_subcomponent_options(self, sub: Any):
        if isinstance(sub, dict):
            return sub.get("options", {})
        else:
            return {}
