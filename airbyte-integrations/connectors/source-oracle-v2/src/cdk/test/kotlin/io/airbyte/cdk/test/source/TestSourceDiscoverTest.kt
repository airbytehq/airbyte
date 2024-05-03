/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.source

import io.airbyte.cdk.consumers.BufferingOutputConsumer
import io.airbyte.cdk.operation.CONNECTOR_OPERATION
import io.airbyte.cdk.operation.DiscoverOperation
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["source"], rebuildContext = true)
@Property(name = CONNECTOR_OPERATION, value = "discover")
class TestSourceDiscoverTest {

    @Inject lateinit var discoverOperation: DiscoverOperation
    @Inject lateinit var outputConsumer: BufferingOutputConsumer

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.cursor", value = "user_defined")
    @Property(name = "metadata.resource", value = "test/source/metadata-valid.json")
    fun testCursorBasedIncremental() {
        val events =
            AirbyteStream()
                .withName("EVENTS")
                .withNamespace("PUBLIC")
                .withJsonSchema(Jsons.deserialize(EVENTS_SCHEMA))
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withDefaultCursorField(listOf("TS"))
                .withSourceDefinedPrimaryKey(listOf(listOf("ID")))
        val kv =
            AirbyteStream()
                .withName("KV")
                .withNamespace("PUBLIC")
                .withJsonSchema(Jsons.deserialize(KV_SCHEMA))
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withDefaultCursorField(listOf("K"))
                .withSourceDefinedPrimaryKey(listOf(listOf("K")))
        val expected = AirbyteCatalog().withStreams(listOf(events, kv))
        discoverOperation.execute()
        Assertions.assertEquals(listOf(expected), outputConsumer.catalogs())
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(name = "airbyte.connector.config.cursor", value = "cdc")
    @Property(name = "metadata.resource", value = "test/source/metadata-valid.json")
    fun testCdcIncremental() {
        // TODO: check that this is indeed the expected behaviour.
        val events =
            AirbyteStream()
                .withName("EVENTS")
                .withNamespace("PUBLIC")
                .withJsonSchema(Jsons.deserialize(EVENTS_SCHEMA))
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withDefaultCursorField(listOf("TS"))
                .withSourceDefinedPrimaryKey(listOf(listOf("ID")))
        val kv =
            AirbyteStream()
                .withName("KV")
                .withNamespace("PUBLIC")
                .withJsonSchema(Jsons.deserialize(KV_SCHEMA))
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withDefaultCursorField(listOf("K"))
                .withSourceDefinedPrimaryKey(listOf(listOf("K")))
        val expected = AirbyteCatalog().withStreams(listOf(events, kv))
        discoverOperation.execute()
        Assertions.assertEquals(listOf(expected), outputConsumer.catalogs())
    }

    companion object {
        const val EVENTS_SCHEMA =
            """
            {
                "type": "object",
                "properties": {
                    "MSG": {
                        "type": "string"
                    },
                    "ID": {
                        "type": "string",
                        "contentEncoding": "base64"
                    },
                    "TS": {
                        "type": "string",
                        "format": "date-time",
                        "airbyte_type": "timestamp_with_timezone"
                    }
                }
            }
        """
        const val KV_SCHEMA =
            """
            {
                "type": "object",
                "properties": {
                    "V": {
                        "type": "string"
                    },
                    "K": {
                        "type": "number",
                        "airbyte_type": "integer"
                    }
                }
            }
        """
    }
}
