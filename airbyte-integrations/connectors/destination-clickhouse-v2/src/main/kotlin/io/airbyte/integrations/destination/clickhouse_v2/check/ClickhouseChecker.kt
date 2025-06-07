package io.airbyte.integrations.destination.clickhouse_v2.check

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse_v2.check.ClickhouseChecker.Constants.TEST_DATA
import io.airbyte.integrations.destination.clickhouse_v2.client.log
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.time.Clock
import java.util.concurrent.TimeUnit

@Singleton
class ClickhouseChecker(
    private val client: Client,
    private val config: ClickhouseConfiguration,
    clock: Clock,
): DestinationChecker {
    // ensure table name unique across checks
    @VisibleForTesting
    val tableName = "_airbyte_check_table_${clock.millis()}"


    override fun check() {
         // TODO: the logic to combine table name database should be codified somewhere ${config.database}.$tableName
         client.execute("CREATE TABLE IF NOT EXISTS ${config.database}.$tableName (test UInt8) ENGINE = MergeTree ORDER BY ()")
             .get(10, TimeUnit.SECONDS)

         val insert =
             client.insert(tableName, TEST_DATA.byteInputStream(), ClickHouseFormat.JSONEachRow)
                 .get(10, TimeUnit.SECONDS)

         assert(insert.writtenRows == 1L) { "Failed to insert expected rows into check table. Actual written: ${insert.writtenRows}" }
    }

    override fun cleanup() {
        try {

            client.execute("DROP TABLE IF EXISTS ${config.database}.$tableName")
                .get(10, TimeUnit.SECONDS)
        } catch (e: Exception) {
            log.error(e) { "Failed to cleanup the check table named ${config.database}.$tableName" }
        }
    }

    object Constants {
        const val TEST_DATA = """{"test": 42}"""
    }
}
