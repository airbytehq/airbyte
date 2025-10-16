# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import patch


def test_schema_loader_uses_cached_schema(components_module):
    with patch.object(components_module.ReportXMLSchemaHelper, "_get_xml_tree", return_value="xml_tree"):
        with patch.object(components_module.ReportXMLSchemaHelper, "_extract_namespace", return_value={}):
            with patch.object(components_module.ReportXMLSchemaHelper, "get_properties", return_value={}) as mock_get_properties:
                schema_loader = components_module.ReportSchemaLoader(
                    {"tenant_id": "tenant_id", "host": "host"},
                    {"report_id": "report_id"},
                )

                schema_loader.get_json_schema()
                # on second call ReportSchemaLoader should get schema from schema property
                # and not call ReportXMLSchemaHelper.get_properties as it could lead to long-running syncs
                schema_loader.get_json_schema()
                assert mock_get_properties.call_count == 1
