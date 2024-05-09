package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.*
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.select.MaxCursorValueQuerier
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQueryGenerator

/** Default implementation of [Worker] for [CursorBasedNotStarted]. */
class CursorBasedColdStartWorker(
        val config: SourceConfiguration,
        selectQueryGenerator: SelectQueryGenerator,
        selectQuerier: SelectQuerier,
        override val input: CursorBasedNotStarted
) : Worker<StreamKey, CursorBasedNotStarted> {

    val maxCursorValueQuerier = MaxCursorValueQuerier(selectQueryGenerator, selectQuerier)

    override fun call(): WorkResult<StreamKey, CursorBasedNotStarted, out StreamState> {
        val maybePrimaryKey: List<Field>? =
            key.configuredPrimaryKey ?: key.primaryKeyCandidates.firstOrNull()
        val cursor: Field =
            (key.configuredCursor ?: key.cursorCandidates.firstOrNull()) as? Field
                ?: throw IllegalStateException("Stream has no cursor.")
        val checkpointValue: JsonNode? = maxCursorValueQuerier.query(key.table, cursor)
        return if (checkpointValue == null) {
            input.completed()
        } else if (maybePrimaryKey != null && config.resumablePreferred) {
            input.resumable(config.initialLimit, maybePrimaryKey, cursor, checkpointValue)
        } else {
            input.nonResumable(cursor, checkpointValue)
        }
    }

    override fun signalStop() {} // unstoppable
}
