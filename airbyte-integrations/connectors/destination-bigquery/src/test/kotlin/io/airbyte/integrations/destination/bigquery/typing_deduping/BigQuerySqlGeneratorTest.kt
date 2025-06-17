/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping

import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQuerySqlGeneratorTest {
    private val generator = BigQuerySqlGenerator("foo", "US")

    @Test
    fun testBuildColumnId() {
        // Uninteresting names are unchanged
        Assertions.assertEquals(ColumnId("foo", "foo", "foo"), generator.buildColumnId("foo"))
    }

    @Test
    fun columnCollision() {
        val parser = CatalogParser(generator, "default_ns")
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        columns[ColumnId("CURRENT_DATE", "CURRENT_DATE", "current_date")] =
            AirbyteProtocolType.STRING
        columns[ColumnId("current_date_1", "current_date", "current_date_1")] =
            AirbyteProtocolType.INTEGER
        Assertions.assertEquals(
            StreamConfig(
                StreamId("bar", "foo", "airbyte_internal", "bar_raw__stream_foo", "bar", "foo"),
                ImportType.APPEND,
                emptyList(),
                Optional.empty(),
                columns,
                1,
                1,
                2
            ),
            parser.toStreamConfig(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withGenerationId(1L)
                    .withMinimumGenerationId(1L)
                    .withSyncId(2L)
                    .withStream(
                        AirbyteStream()
                            .withName("foo")
                            .withNamespace("bar")
                            .withJsonSchema(
                                deserialize(
                                    """
                    {
                      "type": "object",
                      "properties": {
                        "CURRENT_DATE": {"type": "string"},
                        "current_date": {"type": "integer"}
                      }
                    }
                    
                    """.trimIndent()
                                )
                            )
                    )
            )
        )
    }
}
