/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class ConfiguredAirbyteCatalogTest {
    @Inject lateinit var actual: ConfiguredAirbyteCatalog

    @Test
    fun testEmpty() {
        Assertions.assertEquals(ConfiguredAirbyteCatalog(), actual)
    }

    @Test
    @Property(name = "airbyte.connector.catalog.resource", value = CATALOG_RESOURCE)
    fun testInjectedCatalog() {
        val expected =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        "bar",
                                        "foo",
                                        Field.of("id", JsonSchemaType.NUMBER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(listOf("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        "baz",
                                        "foo",
                                        Field.of("id", JsonSchemaType.NUMBER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH)),
                            ),
                    ),
                )
        Assertions.assertEquals(
            Jsons.readTree(ResourceUtils.readResource(CATALOG_RESOURCE)),
            Jsons.valueToTree(expected),
        )
        Assertions.assertEquals(expected, actual)
    }

    companion object {
        const val CATALOG_RESOURCE = "command/catalog.json"
    }
}
