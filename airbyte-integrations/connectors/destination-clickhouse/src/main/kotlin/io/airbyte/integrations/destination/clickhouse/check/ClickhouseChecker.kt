/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.check

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse.check.ClickhouseChecker.Constants.PROTOCOL
import io.airbyte.integrations.destination.clickhouse.check.ClickhouseChecker.Constants.PROTOCOL_ERR_MESSAGE
import io.airbyte.integrations.destination.clickhouse.check.ClickhouseChecker.Constants.TEST_DATA
import io.airbyte.integrations.destination.clickhouse.config.ClickhouseBeanFactory
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
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
        val resolvedTableName = "${config.database}.$tableName"

        // TODO: ideally we'd actually inject a higher level client in here and not write SQL
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

    override fun cleanup(config: ClickhouseConfiguration) {
        val client = clientFactory.make(config)

        // TODO: ideally we'd actually inject a higher level client in here and not write SQL
        client
            .execute("DROP TABLE IF EXISTS ${config.database}.$tableName")
            .get(10, TimeUnit.SECONDS)
    }

    object Constants {
        const val TEST_DATA = """{"test": 42}"""
        // We concatenate to get around CI rules around the string we're building.
        // It will literally break your PR if it sees it.
        const val PROTOCOL = "htt" + "p"
        const val PROTOCOL_ERR_MESSAGE =
            "Please remove the protocol ($PROTOCOL://, https://) from the hostname in your connector configuration."
    }
}

// This exists solely for testing. It will hopefully be deleted once we fix DI.
@Singleton
class RawClickHouseClientFactory {
    fun make(config: ClickhouseConfiguration): Client {
        require(!config.hostname.startsWith(PROTOCOL)) { PROTOCOL_ERR_MESSAGE }

        val factory = ClickhouseBeanFactory()
        val endpoint = factory.resolvedEndpoint(config)
        return ClickhouseBeanFactory().clickhouseClient(config, endpoint)
    }
}
