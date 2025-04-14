package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.DestinationHandler
import io.airbyte.cdk.load.orchestration.TableName
import java.time.Instant

class TypingDedupingFinalTableOperations(
    private val sqlGenerator: TypingDedupingSqlGenerator,
    private val destinationHandler: DestinationHandler,
) {
    fun createFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        suffix: String,
        replace: Boolean
    ) {
        destinationHandler.execute(TODO())
    }

    /** Reset the final table using a temp table or ALTER existing table's columns. */
    fun softResetFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
    ) {
        destinationHandler.execute(TODO())
    }

    /**
     * Attempt to atomically swap the final table from the temp version. This could be destination
     * specific, INSERT INTO..SELECT * and DROP TABLE OR CREATE OR REPLACE ... SELECT *, DROP TABLE
     */
    fun overwriteFinalTable(
        finalTableName: TableName,
        suffix: String,
    ) {
        TODO()
    }

    fun typeAndDedupe(
        stream: DestinationStream,
        rawTableName: TableName,
        finalTableName: TableName,
        maxProcessedTimestamp: Instant?,
        finalTableSuffix: String
    ) {
        TODO()
    }
}
