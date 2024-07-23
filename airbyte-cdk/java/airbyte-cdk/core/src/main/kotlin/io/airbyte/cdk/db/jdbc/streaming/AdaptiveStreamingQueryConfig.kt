/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc.streaming

import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.*

private val LOGGER = KotlinLogging.logger {}

open class AdaptiveStreamingQueryConfig : JdbcStreamingQueryConfig {
    private val fetchSizeEstimator: FetchSizeEstimator = TwoStageSizeEstimator.Companion.instance
    private var currentFetchSize: Int

    init {
        this.currentFetchSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE
    }

    @Throws(SQLException::class)
    override fun initialize(connection: Connection, statement: Statement) {
        connection.autoCommit = false
        statement.fetchSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE
        currentFetchSize = FetchSizeConstants.INITIAL_SAMPLE_SIZE
        LOGGER.info { "Set initial fetch size: ${statement.fetchSize} rows" }
    }

    @Throws(SQLException::class)
    override fun accept(resultSet: ResultSet, rowData: Any) {
        fetchSizeEstimator.accept(rowData)
        val newFetchSize = fetchSizeEstimator.fetchSize

        if (newFetchSize.isPresent && currentFetchSize != newFetchSize.get()) {
            LOGGER.info { "Set new fetch size: ${newFetchSize.get()} rows" }
            resultSet.fetchSize = newFetchSize.get()
            currentFetchSize = newFetchSize.get()
        }
    }
}
