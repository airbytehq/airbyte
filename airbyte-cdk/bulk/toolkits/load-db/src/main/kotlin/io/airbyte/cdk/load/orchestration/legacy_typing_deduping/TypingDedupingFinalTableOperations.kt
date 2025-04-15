/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.DestinationHandler
import io.airbyte.cdk.load.orchestration.TableName
import io.airbyte.cdk.load.orchestration.TableNames
import io.airbyte.cdk.load.orchestration.TableNames.Companion.SOFT_RESET_SUFFIX
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant

private val logger = KotlinLogging.logger {}

class TypingDedupingFinalTableOperations(
    private val sqlGenerator: TypingDedupingSqlGenerator,
    private val destinationHandler: DestinationHandler,
) {
    fun createFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String,
        replace: Boolean
    ) {
        logger.info {
            "Creating final table for stream ${stream.descriptor.toPrettyString()} with name ${finalTableName.prettyPrint()}"
        }
        destinationHandler.execute(
            sqlGenerator.createFinalTable(
                stream,
                finalTableName,
                finalTableSuffix,
                replace = replace
            )
        )
    }

    /** Reset the final table using a temp table or ALTER existing table's columns. */
    fun softResetFinalTable(
        stream: DestinationStream,
        tableNames: TableNames,
    ) {
        logger.info {
            "Executing soft reset for stream ${stream.descriptor.toPrettyString()} on tables ${tableNames.prettyPrint()}"
        }
        destinationHandler.execute(sqlGenerator.prepareTablesForSoftReset(stream, tableNames))
        typeAndDedupe(
            stream,
            tableNames,
            maxProcessedTimestamp = null,
            finalTableSuffix = SOFT_RESET_SUFFIX,
        )
        destinationHandler.execute(
            sqlGenerator.overwriteFinalTable(
                stream,
                tableNames.finalTableName!!,
                finalTableSuffix = SOFT_RESET_SUFFIX
            )
        )
    }

    /**
     * Attempt to atomically swap the final table from the temp version. This could be destination
     * specific, INSERT INTO..SELECT * and DROP TABLE OR CREATE OR REPLACE ... SELECT *, DROP TABLE
     */
    fun overwriteFinalTable(
        stream: DestinationStream,
        finalTableName: TableName,
        finalTableSuffix: String,
    ) {
        logger.info {
            "Overwriting final table for stream ${stream.descriptor.toPrettyString()} with name ${finalTableName.prettyPrint()} using temp table with suffix $finalTableSuffix"
        }
        destinationHandler.execute(
            sqlGenerator.overwriteFinalTable(
                stream,
                finalTableName,
                finalTableSuffix = finalTableSuffix
            )
        )
    }

    fun typeAndDedupe(
        stream: DestinationStream,
        tableNames: TableNames,
        maxProcessedTimestamp: Instant?,
        finalTableSuffix: String
    ) {
        try {
            logger.info {
                "Attempting typing and deduping for stream ${stream.descriptor.toPrettyString()} on tables ${tableNames.prettyPrint()} with suffix $finalTableSuffix"
            }
            val unsafeSql =
                sqlGenerator.updateFinalTable(
                    stream,
                    tableNames,
                    finalTableSuffix = finalTableSuffix,
                    maxProcessedTimestamp = maxProcessedTimestamp,
                    useExpensiveSaferCasting = false,
                )
            destinationHandler.execute(unsafeSql)
        } catch (e: Exception) {
            if (sqlGenerator.supportsExpensiveSaferCasting) {
                logger.info(e) {
                    "Encountered Exception on unsafe SQL for stream ${stream.descriptor.toPrettyString()} on tables ${tableNames.prettyPrint()} with suffix $finalTableSuffix, re-attempting with error handling"
                }
                val saferSql =
                    sqlGenerator.updateFinalTable(
                        stream,
                        tableNames,
                        finalTableSuffix = finalTableSuffix,
                        maxProcessedTimestamp = maxProcessedTimestamp,
                        useExpensiveSaferCasting = true,
                    )
                destinationHandler.execute(saferSql)
            } else {
                logger.info(e) {
                    "Encountered Exception on unsafe SQL for stream ${stream.descriptor.toPrettyString()} on tables ${tableNames.prettyPrint()} with suffix $finalTableSuffix, not retrying"
                }
                throw e
            }
        }
    }
}
