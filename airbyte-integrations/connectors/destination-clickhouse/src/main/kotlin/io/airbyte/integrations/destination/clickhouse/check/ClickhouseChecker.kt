/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.check

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.time.Clock
import java.util.concurrent.TimeUnit

@Singleton
class ClickhouseChecker(
    clock: Clock,
    private val config: ClickhouseConfiguration,
    private val client: Client,
) : DestinationChecker {
    @VisibleForTesting val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check() {
        val resolvedTableName = "${config.database}.$tableName"

        client
            .execute(
                "CREATE TABLE IF NOT EXISTS $resolvedTableName (test UInt8) ENGINE = MergeTree ORDER BY ()"
            )
            .get(10, TimeUnit.SECONDS)

        val insert =
            client
                .insert(
                    resolvedTableName,
                    TEST_DATA.byteInputStream(),
                    ClickHouseFormat.JSONEachRow
                )
                .get(10, TimeUnit.SECONDS)

        require(insert.writtenRows == 1L) {
            "Failed to insert expected rows into check table. Actual written: ${insert.writtenRows}"
        }
    }

    override fun cleanup() {
        client
            .execute("DROP TABLE IF EXISTS ${config.database}.$tableName")
            .get(10, TimeUnit.SECONDS)
    }

    companion object {
        const val TEST_DATA = """{"test": 42}"""
    }
}
