/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.Stream
import io.airbyte.integrations.source.bigqueryv2.BigQuerySourceOperations
import java.time.Instant

/** A [SelectQuerier] that must never be reached by the unit tests. */
object NoSelectQuerier : SelectQuerier {
    override fun executeQuery(
        q: SelectQuery,
        parameters: SelectQuerier.Parameters
    ): SelectQuerier.Result =
        throw UnsupportedOperationException("unit tests must not query BigQuery: ${q.sql}")
}

/**
 * [BigQueryReadApiSnapshotQueries] answering with fixed values, recording what it was asked, so the
 * factory's incremental snapshot planning can be tested without BigQuery.
 */
class FixedSnapshotQueries(
    private val snapshotTime: Instant = Instant.parse("2026-09-22T08:00:00Z"),
    private val upperBound: JsonNode?,
) :
    BigQueryReadApiSnapshotQueries(
        BigQuerySourceOperations("p"),
        NoSelectQuerier,
        ClockFactory().fixed()
    ) {
    val asked: MutableList<Pair<String, Instant>> = mutableListOf()

    override fun pickSnapshotTime(): Instant = snapshotTime

    override fun cursorUpperBound(
        stream: Stream,
        cursor: EmittedField,
        snapshotTime: Instant
    ): JsonNode? {
        asked.add(cursor.id to snapshotTime)
        return upperBound
    }
}
