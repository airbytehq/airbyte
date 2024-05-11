/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import java.time.Instant
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object TypeAndDedupeTransaction {
    const val SOFT_RESET_SUFFIX: String = "_ab_soft_reset"
    private val LOGGER: Logger = LoggerFactory.getLogger(TypeAndDedupeTransaction::class.java)

    /**
     * It can be expensive to build the errors array in the airbyte_meta column, so we first attempt
     * an 'unsafe' transaction which assumes everything is typed correctly. If that fails, we will
     * run a more expensive query which handles casting errors
     *
     * @param sqlGenerator for generating sql for the destination
     * @param destinationHandler for executing sql created
     * @param streamConfig which stream to operate on
     * @param minExtractedAt to reduce the amount of data in the query
     * @param suffix table suffix for temporary tables
     * @throws Exception if the safe query fails
     */
    @JvmStatic
    @Throws(Exception::class)
    fun executeTypeAndDedupe(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig?,
        minExtractedAt: Optional<Instant>,
        suffix: String
    ) {
        try {
            LOGGER.info(
                "Attempting typing and deduping for {}.{} with suffix {}",
                streamConfig!!.id.originalNamespace,
                streamConfig.id.originalName,
                suffix
            )
            val unsafeSql = sqlGenerator.updateTable(streamConfig, suffix, minExtractedAt, false)
            destinationHandler.execute(unsafeSql)
        } catch (e: Exception) {
            if (sqlGenerator.shouldRetry(e)) {
                // TODO Destination specific non-retryable exceptions should be added.
                LOGGER.error(
                    "Encountered Exception on unsafe SQL for stream {} {} with suffix {}, attempting with error handling",
                    streamConfig!!.id.originalNamespace,
                    streamConfig.id.originalName,
                    suffix,
                    e
                )
                val saferSql = sqlGenerator.updateTable(streamConfig, suffix, minExtractedAt, true)
                destinationHandler.execute(saferSql)
            } else {
                LOGGER.error(
                    "Encountered Exception on unsafe SQL for stream {} {} with suffix {}, Retry is skipped",
                    streamConfig!!.id.originalNamespace,
                    streamConfig.id.originalName,
                    suffix,
                    e
                )
                throw e
            }
        }
    }

    /**
     * Everything in [TypeAndDedupeTransaction.executeTypeAndDedupe] but with a little extra prep
     * work for the soft reset temp tables
     *
     * @param sqlGenerator for generating sql for the destination
     * @param destinationHandler for executing sql created
     * @param streamConfig which stream to operate on
     * @throws Exception if the safe query fails
     */
    @JvmStatic
    @Throws(Exception::class)
    fun executeSoftReset(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig
    ) {
        LOGGER.info(
            "Attempting soft reset for stream {} {}",
            streamConfig.id.originalNamespace,
            streamConfig.id.originalName
        )
        destinationHandler.execute(sqlGenerator.prepareTablesForSoftReset(streamConfig))
        executeTypeAndDedupe(
            sqlGenerator,
            destinationHandler,
            streamConfig,
            Optional.empty(),
            SOFT_RESET_SUFFIX
        )
        destinationHandler.execute(
            sqlGenerator.overwriteFinalTable(streamConfig.id, SOFT_RESET_SUFFIX)
        )
    }
}
