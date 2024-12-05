/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.helper

import com.google.common.collect.Lists
import io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration
import io.airbyte.api.client.model.generated.AirbyteStreamConfiguration
import io.airbyte.api.client.model.generated.DestinationSyncMode
import io.airbyte.api.client.model.generated.SyncMode
import io.airbyte.commons.text.Names
import io.airbyte.protocol.models.*
import java.util.List
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

internal class CatalogClientConvertersTest {
    @Test
    fun testConvertToClientAPI() {
        Assertions.assertEquals(
            EXPECTED_CLIENT_CATALOG,
            CatalogClientConverters.toAirbyteCatalogClientApi(BASIC_MODEL_CATALOG)
        )
    }

    @Test
    fun testConvertToProtocol() {
        Assertions.assertEquals(
            BASIC_MODEL_CATALOG,
            CatalogClientConverters.toAirbyteProtocol(EXPECTED_CLIENT_CATALOG)
        )
    }

    companion object {
        const val ID_FIELD_NAME: String = "id"
        private const val STREAM_NAME = "users-data"
        private val STREAM: AirbyteStream =
            AirbyteStream()
                .withName(STREAM_NAME)
                .withJsonSchema(
                    CatalogHelpers.fieldsToJsonSchema(
                        Field.of(ID_FIELD_NAME, JsonSchemaType.STRING)
                    )
                )
                .withDefaultCursorField(Lists.newArrayList(ID_FIELD_NAME))
                .withSourceDefinedCursor(false)
                .withSourceDefinedPrimaryKey(emptyList())
                .withSupportedSyncModes(
                    List.of(
                        io.airbyte.protocol.models.SyncMode.FULL_REFRESH,
                        io.airbyte.protocol.models.SyncMode.INCREMENTAL
                    )
                )

        private val CLIENT_STREAM: io.airbyte.api.client.model.generated.AirbyteStream =
            io.airbyte.api.client.model.generated
                .AirbyteStream()
                .name(STREAM_NAME)
                .jsonSchema(
                    CatalogHelpers.fieldsToJsonSchema(
                        Field.of(ID_FIELD_NAME, JsonSchemaType.STRING)
                    )
                )
                .defaultCursorField(Lists.newArrayList(ID_FIELD_NAME))
                .sourceDefinedCursor(false)
                .sourceDefinedPrimaryKey(emptyList())
                .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        private val CLIENT_DEFAULT_STREAM_CONFIGURATION: AirbyteStreamConfiguration =
            AirbyteStreamConfiguration()
                .syncMode(SyncMode.FULL_REFRESH)
                .cursorField(Lists.newArrayList(ID_FIELD_NAME))
                .destinationSyncMode(DestinationSyncMode.APPEND)
                .primaryKey(emptyList())
                .aliasName(Names.toAlphanumericAndUnderscore(STREAM_NAME))
                .selected(true)

        private val BASIC_MODEL_CATALOG: AirbyteCatalog =
            AirbyteCatalog().withStreams(Lists.newArrayList(STREAM))

        private val EXPECTED_CLIENT_CATALOG: io.airbyte.api.client.model.generated.AirbyteCatalog =
            io.airbyte.api.client.model.generated
                .AirbyteCatalog()
                .streams(
                    Lists.newArrayList(
                        AirbyteStreamAndConfiguration()
                            .stream(CLIENT_STREAM)
                            .config(CLIENT_DEFAULT_STREAM_CONFIGURATION)
                    )
                )
    }
}
