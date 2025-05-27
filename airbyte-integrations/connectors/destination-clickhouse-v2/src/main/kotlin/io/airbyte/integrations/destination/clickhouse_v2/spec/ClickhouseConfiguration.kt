package io.airbyte.integrations.destination.clickhouse_v2.spec

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

data class ClickhouseConfiguration(
    val test: String
): DestinationConfiguration() {
    override val numOpenStreamWorkers: Int = 3
}

@Singleton
class ClickhouseConfigurationFactory :
    DestinationConfigurationFactory<ClickHouseSpecification, ClickhouseConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: ClickHouseSpecification): ClickhouseConfiguration =
        ClickhouseConfiguration("test")
}
