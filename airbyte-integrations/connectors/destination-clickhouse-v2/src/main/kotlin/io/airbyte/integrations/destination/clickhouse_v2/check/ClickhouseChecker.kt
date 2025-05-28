package io.airbyte.integrations.destination.clickhouse_v2.check

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton

@Singleton
class ClickhouseChecker(
    val clickhouseClient: Client,
): DestinationChecker<ClickhouseConfiguration> {
    override fun check(config: ClickhouseConfiguration) {
        // create table
        // write
        // cleanup?
    }
}
