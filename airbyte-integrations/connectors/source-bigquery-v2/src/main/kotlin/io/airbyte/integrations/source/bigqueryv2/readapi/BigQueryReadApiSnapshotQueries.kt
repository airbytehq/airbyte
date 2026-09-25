/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.bigqueryv2.BigQuerySourceOperations
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Instant
import java.time.temporal.ChronoUnit

private val log = KotlinLogging.logger {}

/**
 * The two things the initial snapshot of an incremental stream needs before its read session can be
 * opened: the instant the table is read as of, and the cursor's maximum value at that same instant.
 * Both go through BigQuery time travel, so the Storage Read API session (`snapshot_time`) and the
 * `MAX(cursor)` query (`FOR SYSTEM_TIME AS OF`) see the same table version, whatever gets written
 * in between.
 *
 * `open` so that unit tests can stub it; nothing else should subclass it.
 */
@Singleton
open class BigQueryReadApiSnapshotQueries(
    private val operations: BigQuerySourceOperations,
    private val selectQuerier: SelectQuerier,
    private val clock: Clock,
) {
    /**
     * A little in the past, truncated to microseconds (BigQuery's timestamp precision): a snapshot
     * time in the future is rejected, and the connector's clock may run ahead of BigQuery's.
     */
    open fun pickSnapshotTime(): Instant =
        clock.instant().minusSeconds(SNAPSHOT_LAG_SECONDS).truncatedTo(ChronoUnit.MICROS)

    /**
     * `MAX(cursor)` as of [snapshotTime], as the JSON value the JDBC cursor path would have stored
     * (same getter, same encoder), or null when the table has no non-null cursor value at that
     * instant.
     */
    open fun cursorUpperBound(
        stream: Stream,
        cursor: EmittedField,
        snapshotTime: Instant,
    ): JsonNode? {
        val query: SelectQuery =
            operations.cursorUpperBoundAsOfQuery(
                stream.name,
                stream.namespace,
                cursor,
                snapshotTime
            )
        log.info { "Querying the maximum '${cursor.id}' of '${stream.label}' as of $snapshotTime." }
        val value: JsonNode? =
            selectQuerier.executeQuery(query).use { result ->
                if (result.hasNext()) result.next().data.toJson()[cursor.id] else null
            }
        return value?.takeUnless { it.isNull }
    }

    companion object {
        const val SNAPSHOT_LAG_SECONDS: Long = 2L
    }
}
