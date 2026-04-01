/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import java.time.Duration

/** Shared helpers for SnowflakeSourceOperations unit tests. */
abstract class SnowflakeOperationsBaseTest {

    protected val queryGenerator = SnowflakeSourceOperations()

    protected fun configWith(
        startDate: String? = null,
        endDate: String? = null,
        fullRefreshTemporalColumn: String? = null,
    ) =
        SnowflakeSourceConfiguration(
            realHost = "test.snowflakecomputing.com",
            jdbcUrlFmt = "jdbc:snowflake://%s",
            jdbcProperties = emptyMap(),
            incremental = UserDefinedCursorIncrementalConfiguration,
            maxConcurrency = 1,
            checkpointTargetInterval = Duration.ofSeconds(300),
            checkPrivileges = false,
            startDate = startDate,
            endDate = endDate,
            fullRefreshTemporalColumn = fullRefreshTemporalColumn,
        )
}
