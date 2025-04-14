/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.TableName
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader

class LegacyTypingDedupingStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: TypingDedupingDestinationInitialStatus,
    private val rawTableName: TableName,
    private val finalTableName: TableName,
    private val rawTableOperations: TypingDedupingRawTableOperations,
    private val finalTableOperations: TypingDedupingFinalTableOperations,
) : StreamLoader {

    override suspend fun start() {
        // TODO do all the truncate stuff
        rawTableOperations.prepareRawTable(
            rawTableName,
            suffix = "",
            replace = false,
        )
        finalTableOperations.createFinalTable(
            stream,
            finalTableName,
            suffix = "",
            replace = false,
        )
    }

    override suspend fun close(streamFailure: StreamProcessingFailed?) {
        if (streamFailure == null) {
            // TODO only do this in truncate mode, do all the correct truncate stuff
            rawTableOperations.overwriteRawTable(rawTableName, suffix = "_airbyte_tmp")
            finalTableOperations.typeAndDedupe(
                stream,
                rawTableName,
                finalTableName,
                maxProcessedTimestamp = TODO(),
                finalTableSuffix = "",
            )
            // TODO extract constant for suffix
            finalTableOperations.overwriteFinalTable(finalTableName, suffix = "")
        }
    }
}
