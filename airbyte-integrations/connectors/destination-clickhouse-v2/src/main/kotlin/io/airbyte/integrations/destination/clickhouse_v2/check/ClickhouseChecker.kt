/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.check

import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse_v2.check.ClickhouseChecker.Constants.TEST_DATA
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseBeanFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.time.Clock
import java.util.concurrent.TimeUnit

@Singleton
class ClickhouseChecker(
    clock: Clock,
    private val clientFactory: RawClickHouseClientFactory,
) : DestinationChecker<ClickhouseConfiguration> {
    // ensure table name unique across checks — could factor this out into an injectable shared util
    @VisibleForTesting val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check(config: ClickhouseConfiguration) {
        val client = clientFactory.make(config)

        // TODO: ideally we'd actually inject a higher level client in here and not write SQL
        client
            .execute(
                "CREATE TABLE IF NOT EXISTS ${config.database}.$tableName (test UInt8) ENGINE = MergeTree ORDER BY ()"
            )
            .get(10, TimeUnit.SECONDS)

        val insert =
            client
                .insert(tableName, TEST_DATA.byteInputStream(), ClickHouseFormat.JSONEachRow)
                .get(10, TimeUnit.SECONDS)

        assert(insert.writtenRows == 1L) {
            "Failed to insert expected rows into check table. Actual written: ${insert.writtenRows}"
        }
    }

    override fun cleanup(config: ClickhouseConfiguration) {
        val client = clientFactory.make(config)

        // TODO: ideally we'd actually inject a higher level client in here and not write SQL
        client
            .execute("DROP TABLE IF EXISTS ${config.database}.$tableName")
            .get(10, TimeUnit.SECONDS)
    }

    object Constants {
        const val TEST_DATA = """{"test": 42}"""
    }
}

// This exists solely for testing. It will hopefully be deleted once we fix DI.
@Singleton
class RawClickHouseClientFactory {
    fun make(config: ClickhouseConfiguration) = ClickhouseBeanFactory().clickhouseClient(config)
}
