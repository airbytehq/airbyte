/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.Sql.Companion.of
import java.time.Instant
import java.util.*
import java.util.function.Function

/** Basic SqlGenerator mock. See [DefaultTyperDeduperTest] for example usage. */
internal class MockSqlGenerator : SqlGenerator {
    override fun buildStreamId(
        namespace: String,
        name: String,
        rawNamespaceOverride: String
    ): StreamId {
        throw RuntimeException()
    }

    override fun buildColumnId(name: String, suffix: String?): ColumnId {
        throw RuntimeException()
    }

    override fun createSchema(schema: String): Sql {
        return of("CREATE SCHEMA $schema")
    }

    override fun createTable(stream: StreamConfig, suffix: String, force: Boolean): Sql {
        return of("CREATE TABLE " + stream!!.id.finalTableId("", suffix!!))
    }

    override fun updateTable(
        stream: StreamConfig,
        finalSuffix: String,
        minRawTimestamp: Optional<Instant>,
        useExpensiveSaferCasting: Boolean
    ): Sql {
        val timestampFilter =
            minRawTimestamp
                .map(Function { timestamp: Instant? -> " WHERE extracted_at > $timestamp" })
                .orElse("")
        val casting = if (useExpensiveSaferCasting) " WITH" else " WITHOUT" + " SAFER CASTING"
        return of(
            ("UPDATE TABLE " + stream.id.finalTableId("", finalSuffix)).toString() +
                casting +
                timestampFilter
        )
    }

    override fun overwriteFinalTable(stream: StreamId, finalSuffix: String): Sql {
        return of(
            "OVERWRITE TABLE " +
                stream.finalTableId("") +
                " FROM " +
                stream.finalTableId("", finalSuffix)
        )
    }

    override fun migrateFromV1toV2(streamId: StreamId, namespace: String, tableName: String): Sql {
        return of(
            "MIGRATE TABLE " +
                java.lang.String.join(".", namespace, tableName) +
                " TO " +
                streamId!!.rawTableId("")
        )
    }

    override fun prepareTablesForSoftReset(stream: StreamConfig): Sql {
        return of(
            "PREPARE " +
                java.lang.String.join(".", stream.id.originalNamespace, stream.id.originalName) +
                " FOR SOFT RESET"
        )
    }

    override fun clearLoadedAt(streamId: StreamId): Sql {
        throw RuntimeException()
    }
}
