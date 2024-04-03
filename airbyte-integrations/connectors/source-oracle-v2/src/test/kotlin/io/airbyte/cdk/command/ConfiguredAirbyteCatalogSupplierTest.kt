package io.airbyte.cdk.command

import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, "source"], rebuildContext = true)
class ConfiguredAirbyteCatalogSupplierTest {

    @Inject lateinit var supplier: ConfiguredAirbyteCatalogSupplier

    @Test
    fun testEmpty() {
        Assertions.assertEquals(ConfiguredAirbyteCatalog(), supplier.get())
    }

    @Test
    @Property(name = "airbyte.connector.catalog.json", value = CATALOG_JSON)
    fun testCatalog() {
        val catalog = ConfiguredAirbyteCatalog().withStreams(listOf(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(listOf("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(CatalogHelpers.createAirbyteStream(
                        "bar",
                        "foo",
                        Field.of("id", JsonSchemaType.NUMBER),
                        Field.of("name", JsonSchemaType.STRING))
                        .withSupportedSyncModes(listOf(
                            SyncMode.FULL_REFRESH,
                            SyncMode.INCREMENTAL))),
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(listOf("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(CatalogHelpers.createAirbyteStream(
                        "baz",
                        "foo",
                        Field.of("id", JsonSchemaType.NUMBER),
                        Field.of("name", JsonSchemaType.STRING))
                        .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH)))))
        Assertions.assertEquals(Jsons.deserialize(CATALOG_JSON), Jsons.jsonNode(catalog))
        Assertions.assertEquals(catalog, supplier.get())
    }
}

const val CATALOG_JSON = """
{
  "streams": [
    {
      "stream": {
        "name": "bar",
        "json_schema": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "id": {
              "type": "number"
            }
          }
        },
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ],
        "default_cursor_field": [],
        "source_defined_primary_key": [],
        "namespace": "foo"
      },
      "sync_mode": "incremental",
      "cursor_field": [
        "id"
      ],
      "destination_sync_mode": "append",
      "primary_key": []
    },
    {
      "stream": {
        "name": "baz",
        "json_schema": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string"
            },
            "id": {
              "type": "number"
            }
          }
        },
        "supported_sync_modes": [
          "full_refresh"
        ],
        "default_cursor_field": [],
        "source_defined_primary_key": [],
        "namespace": "foo"
      },
      "sync_mode": "incremental",
      "cursor_field": [
        "id"
      ],
      "destination_sync_mode": "append",
      "primary_key": []
    }
  ]
}
"""
