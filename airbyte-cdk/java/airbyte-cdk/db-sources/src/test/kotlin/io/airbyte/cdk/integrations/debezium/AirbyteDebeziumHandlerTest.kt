/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import com.google.common.collect.Lists
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.util.function.Consumer
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class AirbyteDebeziumHandlerTest {
    @Test
    fun shouldUseCdcTestShouldReturnTrue() {
        val catalog =
            AirbyteCatalog()
                .withStreams(
                    listOf(
                        CatalogHelpers.createAirbyteStream(
                                "MODELS_STREAM_NAME",
                                "MODELS_SCHEMA",
                                Field.of("COL_ID", JsonSchemaType.NUMBER),
                                Field.of("COL_MAKE_ID", JsonSchemaType.NUMBER),
                                Field.of("COL_MODEL", JsonSchemaType.STRING)
                            )
                            .withSupportedSyncModes(
                                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                            )
                            .withSourceDefinedPrimaryKey(listOf(listOf("COL_ID")))
                    )
                )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)
        // set all streams to incremental.
        configuredCatalog.streams.forEach(
            Consumer { s: ConfiguredAirbyteStream -> s.syncMode = SyncMode.INCREMENTAL }
        )

        Assertions.assertTrue(
            AirbyteDebeziumHandler.isAnyStreamIncrementalSyncMode(configuredCatalog)
        )
    }

    @Test
    fun shouldUseCdcTestShouldReturnFalse() {
        val catalog =
            AirbyteCatalog()
                .withStreams(
                    listOf(
                        CatalogHelpers.createAirbyteStream(
                                "MODELS_STREAM_NAME",
                                "MODELS_SCHEMA",
                                Field.of("COL_ID", JsonSchemaType.NUMBER),
                                Field.of("COL_MAKE_ID", JsonSchemaType.NUMBER),
                                Field.of("COL_MODEL", JsonSchemaType.STRING)
                            )
                            .withSupportedSyncModes(
                                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                            )
                            .withSourceDefinedPrimaryKey(listOf(listOf("COL_ID")))
                    )
                )
        val configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog)

        Assertions.assertFalse(
            AirbyteDebeziumHandler.isAnyStreamIncrementalSyncMode(configuredCatalog)
        )
    }
}
