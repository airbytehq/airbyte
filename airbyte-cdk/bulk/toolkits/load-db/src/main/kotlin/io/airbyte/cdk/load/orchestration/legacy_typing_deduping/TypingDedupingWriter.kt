/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.DestinationStatusGatherer
import io.airbyte.cdk.load.orchestration.TableNames
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader

class TypingDedupingWriter(
    private val catalog: DestinationCatalog,
    private val stateGatherer: DestinationStatusGatherer<TypingDedupingDestinationInitialStatus>,
    private val rawTableOperations: TypingDedupingRawTableOperations,
    private val finalTableOperations: TypingDedupingFinalTableOperations,
) : DestinationWriter {
    private lateinit var names: Map<DestinationStream, Pair<TableNames, ColumnNameMapping>>
    private lateinit var initialStatuses:
        Map<DestinationStream, TypingDedupingDestinationInitialStatus>

    override suspend fun setup() {
        // TODO
        //  -1. figure out table/column names
        //   0. gather state
        //   1. execute migrations
        //   2. soft reset
        //   3. gather state
        names = TODO()
        val initialInitialStatuses: Map<DestinationStream, TypingDedupingDestinationInitialStatus> =
            stateGatherer.gatherInitialStatus(names)
        // TODO migrations
        // TODO soft reset if needed
        // TODO only refetch streams that need to be refetched
        initialStatuses = stateGatherer.gatherInitialStatus(names)
    }

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        val tableNames = names[stream]!!.first
        return LegacyTypingDedupingStreamLoader(
            stream,
            initialStatuses[stream]!!,
            tableNames.rawTableName!!,
            tableNames.finalTableName!!,
            rawTableOperations,
            finalTableOperations,
        )
    }
}
