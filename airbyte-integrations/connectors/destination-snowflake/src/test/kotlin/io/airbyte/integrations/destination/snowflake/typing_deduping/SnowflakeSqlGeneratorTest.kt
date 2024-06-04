/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import io.airbyte.commons.json.Jsons.deserialize
import io.airbyte.integrations.base.destination.typing_deduping.*
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.function.Executable

class SnowflakeSqlGeneratorTest {
    private val generator = SnowflakeSqlGenerator(0)

    @Test
    fun columnNameSpecialCharacterHandling() {
        Assertions.assertAll( // If a ${ is present, then we should replace all of $, {, and } with
            // underscores
            Executable {
                Assertions.assertEquals(
                    ColumnId("__FOO_", "\${foo}", "__FOO_"),
                    generator.buildColumnId("\${foo}")
                )
            }, // But normally, we should leave those characters untouched.
            Executable {
                Assertions.assertEquals(
                    ColumnId("{FO\$O}", "{fo\$o}", "{FO\$O}"),
                    generator.buildColumnId("{fo\$o}")
                )
            }
        )
    }

    /** Similar to [.columnNameSpecialCharacterHandling], but for stream name/namespace */
    @Test
    fun streamNameSpecialCharacterHandling() {
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    StreamId(
                        "__FOO_",
                        "__BAR_",
                        "airbyte_internal",
                        "__foo__raw__stream___bar_",
                        "\${foo}",
                        "\${bar}"
                    ),
                    generator.buildStreamId("\${foo}", "\${bar}", "airbyte_internal")
                )
            },
            Executable {
                Assertions.assertEquals(
                    StreamId(
                        "{FO\$O}",
                        "{BA\$R}",
                        "airbyte_internal",
                        "{fo\$o}_raw__stream_{ba\$r}",
                        "{fo\$o}",
                        "{ba\$r}"
                    ),
                    generator.buildStreamId("{fo\$o}", "{ba\$r}", "airbyte_internal")
                )
            }
        )
    }

    @Test
    fun columnCollision() {
        val parser = CatalogParser(generator)
        val expectedColumns = LinkedHashMap<ColumnId, AirbyteType>()
        expectedColumns[ColumnId("_CURRENT_DATE", "CURRENT_DATE", "_CURRENT_DATE")] =
            AirbyteProtocolType.STRING
        expectedColumns[ColumnId("_CURRENT_DATE_1", "current_date", "_CURRENT_DATE_1")] =
            AirbyteProtocolType.INTEGER
        Assertions.assertEquals(
            StreamConfig(
                StreamId("BAR", "FOO", "airbyte_internal", "bar_raw__stream_foo", "bar", "foo"),
                DestinationSyncMode.APPEND,
                emptyList(),
                Optional.empty(),
                expectedColumns,
                0,
                0,
                0
            ),
            parser.toStreamConfig(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
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
