package io.airbyte.cdk.read.stream

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.read.*
import io.airbyte.cdk.source.select.MaxCursorValueQuerier
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQueryGenerator

/** Default implementation of [Worker] for [CursorBasedIncrementalStarting]. */
class CursorBasedWarmStartWorker(
        val config: SourceConfiguration,
        selectQueryGenerator: SelectQueryGenerator,
        selectQuerier: SelectQuerier,
        override val input: CursorBasedIncrementalStarting,
) : Worker<StreamKey, CursorBasedIncrementalStarting> {

    val maxCursorValueQuerier = MaxCursorValueQuerier(selectQueryGenerator, selectQuerier)

    override fun call(): WorkResult<StreamKey, CursorBasedIncrementalStarting, out StreamState> {
        val targetValue: JsonNode = maxCursorValueQuerier.query(key.table, input.cursor)
            ?: throw IllegalStateException("Stream has no cursor data")
        return input.resumable(config.initialLimit, targetValue)
    }

    override fun signalStop() {} // unstoppable
}
