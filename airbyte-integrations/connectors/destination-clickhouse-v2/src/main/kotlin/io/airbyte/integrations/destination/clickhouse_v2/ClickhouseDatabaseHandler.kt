package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.load.orchestration.db.BaseDatabaseHandler
import io.airbyte.cdk.load.orchestration.db.DatabaseHandler
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseAirbyteClient
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@Singleton
class ClickhouseDatabaseHandler(private val clickhouseClient: Client,
    client: ClickhouseAirbyteClient
    ): BaseDatabaseHandler<ClickHouseDataType>(client) {
    override fun execute(sql: Sql) {
        val statement =
            java.lang.String.join("\n", sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT TRANSACTION"))
        clickhouseClient.execute(statement).get()
    }
}
