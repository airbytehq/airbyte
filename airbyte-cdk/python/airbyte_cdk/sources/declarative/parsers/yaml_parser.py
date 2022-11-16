#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import yaml
from airbyte_cdk.sources.declarative.parsers.config_parser import ConnectionDefinitionParser
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.types import ConnectionDefinition


class YamlParser(ConnectionDefinitionParser):
    """
    Parses a Yaml string to a ConnectionDefinition. Because a Yaml manifest might contain references to previously
    defined components, in addition to parsing the manifest, it also undergoes an additional preprocessing step
    to resolve the reference to the corresponding component definition.
    """

    def __init__(self):
        self.reference_resolver = ManifestReferenceResolver()

    def parse(self, connection_definition_str: str) -> ConnectionDefinition:
        """
        Parses a yaml file and dereferences string in the form "*ref({reference)"
        to {reference}
        :param connection_definition_str: yaml string to parse
        :return: The ConnectionDefinition parsed from connection_definition_str
        """
        manifest = yaml.safe_load(connection_definition_str)

        evaluated_definition = {}
        return self.reference_resolver.preprocess_manifest(manifest, evaluated_definition, "")
