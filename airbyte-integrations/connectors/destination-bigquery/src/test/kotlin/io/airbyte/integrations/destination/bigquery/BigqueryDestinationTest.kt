/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.Optional
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigqueryDestinationTest {

    @Test
    fun throwOnBadStream() {
        val exception =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                BigQueryDestination.throwIfAnyUnsupportedPrimaryKeys(
                    false,
                    buildCatalog(DestinationSyncMode.APPEND_DEDUP, 2)
                )
            }
        Assertions.assertEquals(
            """
                JSON-typed columns are not currently supported in primary keys.
                public.users_1: weird_column_1
                public.users_2: weird_column_2
            """.trimIndent(),
            exception.message
        )
    }

    @Test
    fun noThrowOnNonDedup() {
        Assertions.assertDoesNotThrow {
            BigQueryDestination.throwIfAnyUnsupportedPrimaryKeys(
                false,
                buildCatalog(DestinationSyncMode.APPEND)
            )
        }
    }

    @Test
    fun noThrowWhenTypingDedupingDisabled() {
        Assertions.assertDoesNotThrow {
            BigQueryDestination.throwIfAnyUnsupportedPrimaryKeys(
                true,
                buildCatalog(DestinationSyncMode.APPEND_DEDUP)
            )
        }
    }

    private fun buildCatalog(
        destinationSyncMode: DestinationSyncMode,
        numStreams: Int = 1
    ): ParsedCatalog {
        val streams =
            (1..numStreams)
                .map {
                    val pkColumn = ColumnId("", "weird_column_$it", "")
                    StreamConfig(
                        StreamId("", "", "", "", "public", "users_$it"),
                        SyncMode.INCREMENTAL,
                        destinationSyncMode,
                        listOf(pkColumn),
                        Optional.empty(),
                        linkedMapOf(pkColumn to Struct(linkedMapOf()))
                    )
                }
                .toList()
        return ParsedCatalog(streams)
    }
}
