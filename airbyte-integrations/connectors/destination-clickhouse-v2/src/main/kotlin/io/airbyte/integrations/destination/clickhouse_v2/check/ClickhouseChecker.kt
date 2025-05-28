package io.airbyte.integrations.destination.clickhouse_v2.check

import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse_v2.ClickhouseBeanFactory
import io.airbyte.integrations.destination.clickhouse_v2.check.ClickhouseChecker.Constants.TEST_DATA
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.time.Clock
import java.util.concurrent.TimeUnit

@Singleton
class ClickhouseChecker(
    clock: Clock,
): DestinationChecker<ClickhouseConfiguration> {
    // ensure table name unique across checks
    @VisibleForTesting
    val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check(config: ClickhouseConfiguration) {
        val client = ClickhouseBeanFactory().clickhouseClient(config)

        client.execute("CREATE TABLE IF NOT EXISTS ${config.database}.$tableName (test, UInt8)")
            .get(10, TimeUnit.SECONDS)

        val insert = client.insert(tableName, TEST_DATA.byteInputStream(), ClickHouseFormat.JSONEachRow)
            .get(10, TimeUnit.SECONDS)

        assert(insert.writtenRows == 1L) { "Failed to insert rows into check table. Actual written: $insert.writtenRows" }
    }

    override fun cleanup(config: ClickhouseConfiguration) {
        val client = ClickhouseBeanFactory().clickhouseClient(config)

        client.execute("DROP TABLE IF EXISTS ${config.database}.$tableName").get(10, TimeUnit.SECONDS)
    }

    object Constants {
        const val TEST_DATA = """{"test": 42}"""
    }
}
