package io.airbyte.integrations.destination.clickhouse_v2.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import jakarta.inject.Singleton

@Singleton
class ClickhouseChecker: DestinationChecker<ClickhouseConfiguration> {
    override fun check(config: ClickhouseConfiguration) {
        // Do Nothing
    }
}
